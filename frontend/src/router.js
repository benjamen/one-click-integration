import { userResource } from "@/data/user"
import { createRouter, createWebHistory } from "vue-router"
import { session } from "./data/session"

const routes = [
	{
		path: "/",
		name: "Home",
		component: () => import("@/pages/Home.vue"),
	},
	{
		path: "/pricing",
		name: "Pricing",
		component: () => import("@/pages/Pricing.vue"),
	},
	{
		path: "/api",
		name: "API",
		component: () => import("@/pages/APIDocumentation.vue"),
	},
	// New Onboarding Flow
	{
		name: "Auth",
		path: "/auth",
		component: () => import("@/pages/onboarding/AuthView.vue"),
		meta: { isOnboarding: true },
	},
	{
		name: "ConnectApps",
		path: "/connect",
		component: () => import("@/pages/onboarding/ConnectAppsView.vue"),
		meta: { requiresAuth: true, isOnboarding: true, step: 2 },
	},
	{
		name: "Integrate",
		path: "/integrate",
		component: () => import("@/pages/onboarding/IntegrateView.vue"),
		meta: { requiresAuth: true, isOnboarding: true, step: 3 },
	},
	{
		name: "Configure",
		path: "/configure",
		component: () => import("@/pages/onboarding/ConfigureFieldsView.vue"),
		meta: { requiresAuth: true, isOnboarding: true, step: 4 },
	},
	// Legacy Auth Routes (kept for compatibility)
	{
		name: "Login",
		path: "/account/login",
		component: () => import("@/pages/Login.vue"),
	},
	{
		name: "Signup",
		path: "/account/signup",
		component: () => import("@/pages/Signup.vue"),
	},
	{
		name: "EmailVerification",
		path: "/account/verify-email",
		component: () => import("@/pages/EmailVerification.vue"),
	},
	{
		name: "OAuthCallback",
		path: "/oauth/callback",
		component: () => import("@/pages/OAuthCallback.vue"),
	},
	// Dashboard (post-onboarding)
	{
		name: "Dashboard",
		path: "/dashboard",
		component: () => import("@/pages/Dashboard.vue"),
		meta: { requiresAuth: true },
	},
	// Workflow Builder
	{
		name: "WorkflowBuilder",
		path: "/workflow/create",
		component: () => import("@/pages/WorkflowBuilder.vue"),
		meta: { requiresAuth: true },
	},
	// Account Management
	{
		path: "/account",
		component: () => import("@/layouts/AccountLayout.vue"),
		meta: { requiresAuth: true },
		redirect: "/account/profile",
		children: [
			{
				path: "profile",
				name: "AccountProfile",
				component: () => import("@/pages/account/ProfileView.vue"),
			},
			{
				path: "subscription",
				name: "AccountSubscription",
				component: () => import("@/pages/account/SubscriptionView.vue"),
			},
			{
				path: "integrations",
				name: "AccountIntegrations",
				component: () => import("@/pages/account/IntegrationsView.vue"),
			},
			{
				path: "settings",
				name: "AccountSettings",
				component: () => import("@/pages/account/SettingsView.vue"),
			},
			{
				path: "security",
				name: "AccountSecurity",
				component: () => import("@/pages/account/SecurityView.vue"),
			},
			{
				path: "delete",
				name: "AccountDelete",
				component: () => import("@/pages/account/DeleteAccountView.vue"),
			},
		],
	},
]

const router = createRouter({
	history: createWebHistory("/"),
	routes,
})

router.beforeEach(async (to, from, next) => {
	// Public routes that don't require authentication
	const publicRoutes = ["Home", "Pricing", "API", "Auth", "OAuthCallback", "Signup", "Login", "EmailVerification"]

	// Check if user is logged in
	let isLoggedIn = session.isLoggedIn
	try {
		await userResource.promise
		isLoggedIn = session.isLoggedIn
	} catch (error) {
		isLoggedIn = false
	}

	// Protected routes require authentication
	if (to.matched.some(record => record.meta.requiresAuth)) {
		if (!isLoggedIn) {
			// Redirect to auth if not authenticated
			next({ name: "Auth", query: { redirect: to.fullPath } })
			return
		}
	}

	// Redirect authenticated users away from auth routes to dashboard
	if ((to.name === "Auth" || to.name === "Login" || to.name === "Signup") && isLoggedIn) {
		next({ name: "Dashboard" })
		return
	}

	// Allow public routes without authentication
	if (publicRoutes.includes(to.name)) {
		next()
		return
	}

	next()
})

export default router
