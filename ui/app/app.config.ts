export default defineAppConfig({
  site: {
    name: "Sms Sender",
    motto: "Just send",
    title: "Sms Sender",
    description: "",
    image: "",
    icon: "",
    url: "",
    sourceLink: "https://github.com/PlaceMeIn",
    apiBase: ""
  },
  global: {
    picture: {
      dark:'https://images.unsplash.com/photo-1646766677899-9c1750e28b0f?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8c21zfGVufDB8fDB8fHww',
      light: 'https://images.unsplash.com/photo-1646766677899-9c1750e28b0f?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8c21zfGVufDB8fDB8fHww',
      alt: 'My profile picture'
    },
    meetingLink: 'https://cal.com/',
    email: 'ui-pro@nuxt.com',
    available: true
  },
  ui: {
    colors: {
      primary: 'blue',
      neutral: 'neutral'
    },
    pageHero: {
      slots: {
        container: 'py-18 sm:py-24 lg:py-32',
        title: 'mx-auto max-w-xl text-pretty text-3xl sm:text-4xl lg:text-5xl',
        description: 'mt-2 text-md mx-auto max-w-2xl text-pretty sm:text-md text-muted'
      }
    }
  },
  footer: {
    credits: `Built  • © ${new Date().getFullYear()}`,
    colorMode: false,
    links: [ {
      'icon': 'i-simple-icons-github',
      'to': 'https://github.com/NicholasTecmoverai',
      'target': '_blank',
      'aria-label': 'Nuxt UI on GitHub'
    }]
  }
})
