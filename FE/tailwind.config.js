/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html","./src/**/*.{html,js,vue,ts}"],
  theme: {
    extend: {
      
    },
    // screens: {
    //   sm:'360px'
    // }
  },
  plugins: [],
  corePlugins: {
    // 禁用默认的预设样式，以便添加自定义的全局样式
    preflight: {
      h2:false
    }, 
  },
}

