import path from "node:path"
import vue from "@vitejs/plugin-vue"
import frappeui from "frappe-ui/vite"
import { defineConfig } from "vite"

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => ({
	// Base path: "/" for dev, "/assets/lodgeick/frontend/" for production
	// In dev mode, Vite serves from root, in production Frappe serves from /assets/
	base: command === 'serve' ? '/' : '/assets/lodgeick/frontend/',
	plugins: [
		frappeui({
			lucideIcons: true,
		}),
		vue(),
	],
	build: {
		chunkSizeWarningLimit: 1500,
		outDir: "../lodgeick/public/frontend",
		emptyOutDir: true,
		target: "es2015",
		sourcemap: true,
		// Ensure assets use absolute paths from the /assets/ directory
		assetsDir: "assets",
		rollupOptions: {
			output: {
				manualChunks(id) {
					// Vendor chunk for core Vue libraries
					if (id.includes('node_modules')) {
						if (id.includes('vue') || id.includes('pinia') || id.includes('vue-router')) {
							return 'vendor';
						}
						// frappe-ui into its own chunk
						if (id.includes('frappe-ui')) {
							return 'frappe-ui';
						}
						// All other node_modules into a separate chunk
						return 'vendor-libs';
					}
					// Base UI components into their own chunk
					if (id.includes('src/components/base/')) {
						return 'ui-components';
					}
				},
			},
		},
	},
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "src"),
			"tailwind.config.js": path.resolve(__dirname, "tailwind.config.js"),
		},
	},
	optimizeDeps: {
		include: ["feather-icons", "showdown", "highlight.js/lib/core", "interactjs"],
	},
	server: {
		host: '0.0.0.0',
		port: 5173,
		// Prevent Vite from clearing screen on restart
		clearScreen: false,
		// Allow serving files from Frappe's public directory
		fs: {
			strict: false,
		},
		proxy: {
			// Proxy backend routes to Frappe
			// IMPORTANT: Don't use Vite dev server for /desk or /app routes
			// Access them directly at http://localhost:8090/desk instead
			"^/(app|api|assets|files|desk)": {
				target: "http://127.0.0.1:8090",
				ws: true,
				changeOrigin: true,
				// Don't rewrite path - keep as-is
				rewrite: (path) => path,
			},
		},
	},
}))
