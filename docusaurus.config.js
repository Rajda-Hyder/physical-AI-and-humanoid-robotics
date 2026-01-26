// @ts-check
import {themes as prismThemes} from 'prism-react-renderer';
import dotenv from 'dotenv';
dotenv.config();

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Learn to build and control the future of embodied intelligence',
  favicon: 'img/favicon.ico',

  url: 'https://your-github-username.github.io',
  baseUrl: '/',

  organizationName: 'panaversity',
  projectName: 'physical-ai-robotics',

  onBrokenLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.js',
          editUrl: 'https://github.com/panaversity/physical-ai-robotics/edit/main/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      },
    ],
  ],

  themeConfig: {
    image: 'img/cover/book-cover.svg',
    navbar: {
      title: 'Physical AI & Humanoid Robotics',
      logo: {
        alt: 'Panaversity Logo',
        src: 'img/logo.svg',
      },
      items: [
        {type: 'docSidebar', sidebarId: 'tutorialSidebar', position: 'left', label: 'Learn'},
        {to: '/dashboard', label: 'Dashboard', position: 'right'},
        {to: '/login', label: 'Sign In', position: 'right'},
        {href: 'https://github.com/panaversity/physical-ai-robotics', label: 'GitHub', position: 'right'},
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {label: 'Module 1: Foundations', to: '/docs/module-1-foundations/lesson-1-1-intro-to-physical-ai'},
            {label: 'Module 2: Embodied Robotics', to: '/docs/module-2-embodied-robotics/lesson-2-1-sensing-taking-action'},
            {label: 'Module 3: Humanoid Agents', to: '/docs/module-3-humanoid-ai-agents/lesson-3-1-building-human-like-robots'},
            {label: 'Module 4: Applied Systems', to: '/docs/module-4-applied-ai-native/lesson-4-1-simulation-to-reality'},
          ],
        },
        {title: 'Community', items: [{label: 'GitHub', href: 'https://github.com/panaversity'}]},
        {title: 'More', items: [{label: 'GitHub Repository', href: 'https://github.com/panaversity/physical-ai-robotics'}]},
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Panaversity. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
    colorMode: {
      defaultMode: 'dark',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },
  },

  // ✅ Load runtime environment from static/env.js
  plugins: [
    function envPlugin() {
      return {
        name: 'env-plugin',
        injectHtmlTags() {
          return {
            headTags: [
              {
                tagName: 'script',
                attributes: { src: '/env.js', async: false },
              },
            ],
          };
        },
      };
    },
  ],
};

export default config;
