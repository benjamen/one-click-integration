"""
N8N Integration Sync Service
Synchronizes Lodgeick integrations with n8n workflows
"""

import frappe
import json
from typing import Dict, Optional, Any
from frappe import _
from lodgeick.services.n8n_client import get_n8n_client


class N8NIntegrationSync:
	"""Service to sync Lodgeick integrations with n8n workflows"""

	def __init__(self):
		"""Initialize sync service"""
		self.client = get_n8n_client()

	# ==================== Node Configuration Mapping ====================

	def _get_node_config_for_app(self, app_type: str, settings: Dict) -> Dict:
		"""
		Map Lodgeick app settings to n8n node configuration

		Args:
			app_type: Application type (e.g., 'slack', 'google_sheets')
			settings: Lodgeick integration settings

		Returns:
			n8n node configuration
		"""
		# Map app types to n8n node types
		node_type_map = {
			"slack": "n8n-nodes-base.slack",
			"google_sheets": "n8n-nodes-base.googleSheets",
			"google_drive": "n8n-nodes-base.googleDrive",
			"gmail": "n8n-nodes-base.gmail",
			"jira": "n8n-nodes-base.jira",
			"hubspot": "n8n-nodes-base.hubspot",
			"xero": "n8n-nodes-base.xero",
			"notion": "n8n-nodes-base.notion",
			"salesforce": "n8n-nodes-base.salesforce",
			"mailchimp": "n8n-nodes-base.mailchimp",
		}

		node_type = node_type_map.get(app_type, f"n8n-nodes-base.{app_type}")

		# Base node configuration
		node_config = {
			"parameters": self._map_settings_to_parameters(app_type, settings),
			"name": app_type.replace("_", " ").title(),
			"type": node_type,
			"typeVersion": 1,
			"position": [250, 300]
		}

		return node_config

	def _map_settings_to_parameters(self, app_type: str, settings: Dict) -> Dict:
		"""
		Map Lodgeick settings to n8n node parameters

		Args:
			app_type: Application type
			settings: Integration settings

		Returns:
			n8n node parameters
		"""
		# App-specific parameter mapping
		parameter_maps = {
			"slack": {
				"channel": settings.get("channel", "#general"),
				"text": settings.get("message_template", "{{$json.message}}"),
				"attachments": settings.get("attachments", [])
			},
			"google_sheets": {
				"sheetId": settings.get("spreadsheet_id"),
				"range": settings.get("range", "Sheet1!A1:Z1000"),
				"valueInputOption": settings.get("value_input_option", "USER_ENTERED")
			},
			"gmail": {
				"to": settings.get("recipient"),
				"subject": settings.get("subject_template", "{{$json.subject}}"),
				"message": settings.get("body_template", "{{$json.body}}")
			},
			"jira": {
				"project": settings.get("project_key"),
				"issueType": settings.get("issue_type", "Task"),
				"summary": settings.get("summary_template", "{{$json.title}}")
			}
		}

		return parameter_maps.get(app_type, settings)

	def _build_workflow_json(self, integration_doc: Any) -> Dict:
		"""
		Build complete n8n workflow JSON from integration

		Args:
			integration_doc: Frappe User Integration document

		Returns:
			n8n workflow configuration
		"""
		# Parse config JSON
		try:
			config = json.loads(integration_doc.config) if integration_doc.config else {}
		except json.JSONDecodeError:
			config = {}

		# Determine trigger type from config
		trigger_type = config.get("trigger", "manual")
		schedule = config.get("schedule", "hourly")

		# Build trigger node based on type
		if trigger_type == "schedule":
			trigger_node = self._build_schedule_trigger_node(integration_doc.name, schedule)
		elif trigger_type == "realtime":
			trigger_node = self._build_webhook_trigger_node(integration_doc.name)
		else:  # manual
			trigger_node = self._build_manual_trigger_node(integration_doc.name)

		# Build source node with resource and field selection
		source_node = self._build_source_node(
			integration_doc.source_app,
			config.get("sourceResource"),
			config.get("sourceFields", []),
			config.get("source_settings", {})
		)

		# Build field mapping node if mappings exist
		field_mappings = config.get("fieldMappings", [])
		nodes = [trigger_node, source_node]
		connections = {}

		if field_mappings:
			# Add Set node for field mapping
			mapping_node = self._build_field_mapping_node(field_mappings)
			nodes.append(mapping_node)

			# Connect: Trigger -> Source -> Mapping
			connections = {
				trigger_node["name"]: {
					"main": [[{"node": source_node["name"], "type": "main", "index": 0}]]
				},
				source_node["name"]: {
					"main": [[{"node": mapping_node["name"], "type": "main", "index": 0}]]
				}
			}
			previous_node = mapping_node["name"]
		else:
			# Connect: Trigger -> Source
			connections = {
				trigger_node["name"]: {
					"main": [[{"node": source_node["name"], "type": "main", "index": 0}]]
				}
			}
			previous_node = source_node["name"]

		# Build target node with resource and field selection
		target_node = self._build_target_node(
			integration_doc.target_app,
			config.get("destinationResource"),
			config.get("destinationFields", []),
			config.get("target_settings", {})
		)
		nodes.append(target_node)

		# Connect to target
		connections[previous_node] = {
			"main": [[{"node": target_node["name"], "type": "main", "index": 0}]]
		}

		# Complete workflow structure
		workflow_data = {
			"name": f"Lodgeick: {integration_doc.flow_name}",
			"nodes": nodes,
			"connections": connections,
			"active": integration_doc.status == "Active",
			"settings": {
				"executionOrder": "v1"
			}
		}

		return workflow_data

	def _build_manual_trigger_node(self, integration_name: str) -> Dict:
		"""Build manual trigger node"""
		return {
			"parameters": {},
			"name": "Manual Trigger",
			"type": "n8n-nodes-base.manualTrigger",
			"typeVersion": 1,
			"position": [50, 300]
		}

	def _build_schedule_trigger_node(self, integration_name: str, schedule: str) -> Dict:
		"""Build schedule trigger node"""
		# Map schedule strings to cron expressions
		cron_map = {
			"15min": "*/15 * * * *",
			"hourly": "0 * * * *",
			"daily": "0 0 * * *",
			"weekly": "0 0 * * 0"
		}

		return {
			"parameters": {
				"rule": {
					"interval": [{
						"cronExpression": cron_map.get(schedule, "0 * * * *")
					}]
				}
			},
			"name": "Schedule Trigger",
			"type": "n8n-nodes-base.scheduleTrigger",
			"typeVersion": 1,
			"position": [50, 300]
		}

	def _build_webhook_trigger_node(self, integration_name: str) -> Dict:
		"""Build webhook trigger node"""
		return {
			"parameters": {
				"httpMethod": "POST",
				"path": f"lodgeick-{integration_name}",
				"responseMode": "onReceived",
				"responseData": "firstEntryJson"
			},
			"name": "Webhook Trigger",
			"type": "n8n-nodes-base.webhook",
			"typeVersion": 1,
			"position": [50, 300],
			"webhookId": f"lodgeick-{integration_name}"
		}

	def _build_source_node(self, app_type: str, resource: Dict, fields: list, settings: Dict) -> Dict:
		"""Build source node with resource and field configuration"""
		node_config = self._get_node_config_for_app(app_type, settings)
		node_config["name"] = f"Get from {app_type.replace('_', ' ').title()}"
		node_config["position"] = [300, 300]

		# Add resource-specific parameters
		if resource:
			node_config["parameters"]["resource"] = resource.get("id")
			node_config["parameters"]["operation"] = "getAll"  # Fetch data

		# Add field selection if specified
		if fields:
			node_config["parameters"]["fields"] = fields

		return node_config

	def _build_target_node(self, app_type: str, resource: Dict, fields: list, settings: Dict) -> Dict:
		"""Build target node with resource and field configuration"""
		node_config = self._get_node_config_for_app(app_type, settings)
		node_config["name"] = f"Send to {app_type.replace('_', ' ').title()}"
		node_config["position"] = [700, 300]

		# Add resource-specific parameters
		if resource:
			node_config["parameters"]["resource"] = resource.get("id")
			node_config["parameters"]["operation"] = "create"  # Insert data

		return node_config

	def _build_field_mapping_node(self, field_mappings: list) -> Dict:
		"""Build Set node for field mapping"""
		# Transform field mappings to n8n Set node format
		values = []
		for idx, mapping in enumerate(field_mappings):
			if mapping:  # Skip empty mappings
				values.append({
					"name": mapping,  # Destination field
					"value": f"={{{{$json[\"{idx}\"]}}}}",  # Source field by index
					"type": "string"
				})

		return {
			"parameters": {
				"mode": "manual",
				"duplicateItem": False,
				"assignments": {
					"assignments": values
				}
			},
			"name": "Map Fields",
			"type": "n8n-nodes-base.set",
			"typeVersion": 3,
			"position": [500, 300]
		}

	# ==================== Sync Operations ====================

	def sync_integration_create(self, integration_doc: Any) -> str:
		"""
		Create workflow in n8n when integration is created

		Args:
			integration_doc: Frappe User Integration document

		Returns:
			n8n workflow ID (or None if n8n not available)

		Raises:
			Exception: If workflow creation fails
		"""
		# Check if n8n is enabled
		if not self.client.is_enabled():
			frappe.logger().info(f"n8n integration disabled - workflow {integration_doc.flow_name} created in Lodgeick only")
			integration_doc.status = "Paused"
			integration_doc.error_message = "n8n not configured - workflow saved locally only"
			integration_doc.save(ignore_permissions=True)
			frappe.db.commit()
			return None

		try:
			# Build workflow configuration
			workflow_data = self._build_workflow_json(integration_doc)

			# Remove 'active' field - it's read-only on creation
			should_activate = workflow_data.pop("active", False)

			# Create workflow in n8n
			response = self.client.create_workflow(workflow_data)

			workflow_id = response.get("id")

			if not workflow_id:
				raise Exception("n8n did not return workflow ID")

			# Update integration with workflow ID
			integration_doc.workflow_id = str(workflow_id)
			integration_doc.save(ignore_permissions=True)
			frappe.db.commit()

			# Activate if needed
			if should_activate:
				try:
					self.client.activate_workflow(workflow_id)
				except Exception as activate_error:
					# If activation fails, log but don't fail the whole creation
					frappe.logger().warning(f"Created workflow {workflow_id} but failed to activate: {str(activate_error)}")

			frappe.logger().info(f"Created n8n workflow {workflow_id} for integration {integration_doc.name}")

			return workflow_id

		except Exception as e:
			# Truncate error message to avoid CharacterLengthExceededError
			error_msg = str(e)[:500] if len(str(e)) > 500 else str(e)

			frappe.logger().error(f"Failed to create n8n workflow for {integration_doc.name}: {error_msg}")

			# Try to log error without failing
			try:
				frappe.log_error(f"Failed to create n8n workflow: {error_msg}", "N8N Sync Error")
			except:
				pass  # Ignore if error logging fails

			# Mark integration but don't fail - allow it to be created without n8n
			integration_doc.status = "Paused"
			integration_doc.error_message = f"n8n sync failed: {error_msg}"
			integration_doc.save(ignore_permissions=True)
			frappe.db.commit()

			# Don't raise - allow integration to be created even if n8n fails
			return None

	def sync_integration_update(self, integration_doc: Any) -> bool:
		"""
		Update workflow in n8n when integration is updated

		Args:
			integration_doc: Frappe User Integration document

		Returns:
			True if successful

		Raises:
			Exception: If workflow update fails
		"""
		if not integration_doc.workflow_id:
			# If no workflow exists, create one
			self.sync_integration_create(integration_doc)
			return True

		try:
			# Build updated workflow configuration
			workflow_data = self._build_workflow_json(integration_doc)

			# Update workflow in n8n
			self.client.update_workflow(integration_doc.workflow_id, workflow_data)

			# Clear error state if update successful
			if integration_doc.error_message:
				integration_doc.error_message = None
				integration_doc.save(ignore_permissions=True)
				frappe.db.commit()

			frappe.logger().info(f"Updated n8n workflow {integration_doc.workflow_id} for integration {integration_doc.name}")

			return True

		except Exception as e:
			error_msg = f"Failed to update n8n workflow: {str(e)}"
			frappe.log_error(error_msg, "N8N Sync Error")
			integration_doc.status = "Error"
			integration_doc.error_message = error_msg
			integration_doc.save(ignore_permissions=True)
			frappe.db.commit()
			raise

	def sync_integration_delete(self, integration_doc: Any) -> bool:
		"""
		Delete workflow from n8n when integration is deleted

		Args:
			integration_doc: Frappe User Integration document

		Returns:
			True if successful
		"""
		if not integration_doc.workflow_id:
			# No workflow to delete
			return True

		try:
			# Delete workflow from n8n
			self.client.delete_workflow(integration_doc.workflow_id)

			frappe.logger().info(f"Deleted n8n workflow {integration_doc.workflow_id} for integration {integration_doc.name}")

			return True

		except Exception as e:
			error_msg = f"Failed to delete n8n workflow: {str(e)}"
			frappe.log_error(error_msg, "N8N Sync Error")
			# Don't prevent integration deletion if n8n delete fails
			# Just log the error
			return False

	def sync_integration_status(self, integration_doc: Any, new_status: str) -> bool:
		"""
		Sync integration status to n8n (activate/deactivate workflow)

		Args:
			integration_doc: Frappe User Integration document
			new_status: New status ("Active" or "Paused")

		Returns:
			True if successful
		"""
		if not integration_doc.workflow_id:
			return False

		try:
			if new_status == "Active":
				self.client.activate_workflow(integration_doc.workflow_id)
			else:
				self.client.deactivate_workflow(integration_doc.workflow_id)

			frappe.logger().info(f"Set n8n workflow {integration_doc.workflow_id} status to {new_status}")

			return True

		except Exception as e:
			error_msg = f"Failed to update n8n workflow status: {str(e)}"
			frappe.log_error(error_msg, "N8N Sync Error")
			raise

	# ==================== Credential Sync ====================

	def sync_oauth_credentials(self, provider: str, user: str, token_data: Dict) -> str:
		"""
		Create or update OAuth credentials in n8n

		Args:
			provider: OAuth provider (e.g., 'google', 'slack')
			user: Frappe user
			token_data: OAuth token data

		Returns:
			n8n credential ID
		"""
		# Map provider to n8n credential type
		credential_type_map = {
			"google": "googleOAuth2Api",
			"slack": "slackOAuth2Api",
			"xero": "xeroOAuth2Api",
			"hubspot": "hubspotOAuth2Api"
		}

		credential_type = credential_type_map.get(provider, f"{provider}OAuth2Api")

		credential_data = {
			"name": f"Lodgeick {provider.title()} - {user}",
			"type": credential_type,
			"data": {
				"accessToken": token_data.get("access_token"),
				"refreshToken": token_data.get("refresh_token"),
				"tokenType": token_data.get("token_type", "Bearer"),
				"expiresIn": token_data.get("expires_in")
			}
		}

		try:
			# Check if credential already exists for this user/provider
			existing_credentials = self.client.list_credentials()
			existing_cred = None

			for cred in existing_credentials:
				if cred.get("name") == credential_data["name"]:
					existing_cred = cred
					break

			if existing_cred:
				# Update existing credential
				response = self.client.update_credential(existing_cred["id"], credential_data)
			else:
				# Create new credential
				response = self.client.create_credential(credential_data)

			credential_id = response.get("id")

			frappe.logger().info(f"Synced {provider} credentials to n8n for user {user}")

			return str(credential_id)

		except Exception as e:
			error_msg = f"Failed to sync credentials to n8n: {str(e)}"
			frappe.log_error(error_msg, "N8N Credential Sync Error")
			raise


def get_n8n_sync_service() -> N8NIntegrationSync:
	"""
	Get singleton instance of N8N sync service

	Returns:
		N8NIntegrationSync instance
	"""
	if not hasattr(frappe.local, "n8n_sync_service"):
		frappe.local.n8n_sync_service = N8NIntegrationSync()
	return frappe.local.n8n_sync_service
