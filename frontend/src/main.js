// Initialize frappe shim BEFORE any imports that might use it
// This MUST be the very first code that runs
;(() => {
	if (window.frappe) {
		console.log('[Frappe Shim] Already initialized')
		return
	}

	console.log('[Frappe Shim] Initializing...')

	window.frappe = {
		_messages: {},
		boot: { lang: 'en', sysdefaults: {}, user: {} },
		csrf_token: null,
		datetime: {},
		form: {},
		listview_settings: {},
		model: {
			docinfo: {},
			get_docinfo: function() { return {} },
			get_value: function() { return Promise.resolve() },
			set_value: function() { return Promise.resolve() },
		},
		pages: {},
		provide: function() {},
		require: function() { return Promise.resolve() },
		route_options: null,
		templates: {},
		ui: {
			ScriptManager: function() {
				this.load = function() { return Promise.resolve() }
				this.loaded = {}
			},
			FieldGroup: function() {},
			Dialog: function() {},
			form_builders: {},
			toolbar: {},
		},
		utils: {
			get_url_arg: function() { return null },
			get_query_params: function() { return {} },
		},
		call: function() { return Promise.resolve({ message: {} }) },
		xcall: function() { return Promise.resolve() },
		db: {
			get_value: function() { return Promise.resolve() },
			get_list: function() { return Promise.resolve([]) },
		},
	}
	window.site_name = 'lodgeick.com'
	window.cur_frm = null
	window.cur_list = null
	window.cur_dialog = null

	console.log('[Frappe Shim] Initialized successfully')
})()

import { createApp } from "vue"
import { createPinia } from "pinia"

import App from "./App.vue"
import router from "./router"
import { initSocket } from "./socket"

import {
	Alert,
	Badge,
	Button,
	Card,
	Dialog,
	ErrorMessage,
	FormControl,
	Input,
	TextInput,
	frappeRequest,
	pageMetaPlugin,
	resourcesPlugin,
	setConfig,
} from "frappe-ui"

import "./index.css"
import "./styles/design-tokens.css"
// Note: Bootstrap JavaScript removed - using Tailwind CSS only
// Bootstrap CSS kept for legacy components during migration

// Toast notifications
import Toast from "vue-toastification"
import "vue-toastification/dist/index.css"

const globalComponents = {
	Button,
	Card,
	TextInput,
	Input,
	FormControl,
	ErrorMessage,
	Dialog,
	Alert,
	Badge,
}

const app = createApp(App)
const pinia = createPinia()

setConfig("resourceFetcher", frappeRequest)

app.use(pinia)
app.use(router)
app.use(resourcesPlugin)
app.use(pageMetaPlugin)

// Configure toast notifications
app.use(Toast, {
	position: "top-right",
	timeout: 5000,
	closeOnClick: true,
	pauseOnFocusLoss: true,
	pauseOnHover: true,
	draggable: true,
	draggablePercent: 0.6,
	showCloseButtonOnHover: false,
	hideProgressBar: false,
	closeButton: "button",
	icon: true,
	rtl: false,
	transition: "Vue-Toastification__bounce",
	maxToasts: 5,
	newestOnTop: true
})

const socket = initSocket()
app.config.globalProperties.$socket = socket

for (const key in globalComponents) {
	app.component(key, globalComponents[key])
}

app.mount("#app")
