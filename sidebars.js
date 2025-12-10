/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Module 1: Foundations of Physical AI',
      items: [
        'module-1-foundations/lesson-1-1-intro-to-physical-ai',
        'module-1-foundations/lesson-1-2-software-vs-embodied-ai',
        'module-1-foundations/lesson-1-3-essential-foundational-concepts',
      ],
    },
    {
      type: 'category',
      label: 'Module 2: Embodied Intelligence & Robotics Core',
      items: [
        'module-2-embodied-robotics/lesson-2-1-sensing-taking-action',
        'module-2-embodied-robotics/lesson-2-2-control-systems',
        'module-2-embodied-robotics/lesson-2-3-physical-world-engagement',
      ],
    },
    {
      type: 'category',
      label: 'Module 3: Humanoid Robotics & AI Agents',
      items: [
        'module-3-humanoid-ai-agents/lesson-3-1-building-human-like-robots',
        'module-3-humanoid-ai-agents/lesson-3-2-intelligent-minds-physical-bodies',
        'module-3-humanoid-ai-agents/lesson-3-3-robots-think-move',
      ],
    },
    {
      type: 'category',
      label: 'Module 4: Applied Systems & AI-Native Learning',
      items: [
        'module-4-applied-ai-native/lesson-4-1-simulation-to-reality',
        'module-4-applied-ai-native/lesson-4-2-rag-chatbot-usage',
        'module-4-applied-ai-native/lesson-4-3-tailored-global-learning',
      ],
    },
  ],
};

module.exports = sidebars;
