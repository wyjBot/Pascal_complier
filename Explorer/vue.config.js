const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
    publicPath: '.',
    productionSourceMap: false,
    css: {
        extract: false,
    },
    chainWebpack: (config) => {
        config.plugins.delete('prefetch')
        config.plugins.delete('preload')
    },
    devServer: {
        proxy: {
            '/v2': {
                // target: 'http://localhost:5000',
                changeOrigin:true,
                target: 'http://192.168.234.128:5000',
            },
        },
    },
})
