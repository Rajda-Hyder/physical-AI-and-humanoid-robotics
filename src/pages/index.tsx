import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import HomepageHero from '../components/HomepageHero/HomepageHero';
import ModuleCard from '../components/ModuleCard/ModuleCard';
import FeaturesSection from '../components/FeaturesSection/FeaturesSection';
import styles from './index.module.css';

const modules = [
  {
    moduleNumber: 1,
    title: 'Foundations of Physical AI',
    description:
      'Begin your journey by understanding the fundamentals of Physical AI, embodied intelligence, and the differences between software-only AI and embodied AI systems.',
    learningGoals: [
      'Define Physical AI and embodiment',
      'Understand AI in physical systems',
      'Distinguish software vs. embodied approaches',
    ],
    icon: '/img/module-1/icon.svg',
    firstLessonUrl: '/docs/module-1-foundations/lesson-1-1-intro-to-physical-ai',
  },
  {
    moduleNumber: 2,
    title: 'Embodied Intelligence & Robotics Core',
    description:
      'Explore the sensing, actuation, and control systems that enable robots to perceive their environment and take intelligent actions.',
    learningGoals: [
      'Master sensors and actuators',
      'Learn control systems and feedback',
      'Understand robot-world interaction',
    ],
    icon: '/img/module-2/icon.svg',
    firstLessonUrl: '/docs/module-2-embodied-robotics/lesson-2-1-sensing-taking-action',
  },
  {
    moduleNumber: 3,
    title: 'Humanoid Robotics & AI Agents',
    description:
      'Discover how humanoid robots are designed to mimic human behavior and how AI agents control complex physical systems.',
    learningGoals: [
      'Design human-like robots',
      'Understand AI decision-making',
      'Master navigation and planning',
    ],
    icon: '/img/module-3/icon.svg',
    firstLessonUrl: '/docs/module-3-humanoid-ai-agents/lesson-3-1-building-human-like-robots',
  },
  {
    moduleNumber: 4,
    title: 'Applied Systems & AI-Native Learning',
    description:
      'Learn how to deploy AI from simulation to real robots, integrate RAG chatbots, and personalize learning experiences globally.',
    learningGoals: [
      'Deploy Sim2Real solutions',
      'Integrate RAG chatbot assistance',
      'Adapt content globally',
    ],
    icon: '/img/module-4/icon.svg',
    firstLessonUrl: '/docs/module-4-applied-ai-native/lesson-4-1-simulation-to-reality',
  },
];

const features = [
  {
    icon: '/img/features/hands-on.svg',
    title: 'Hands-on Learning',
    description:
      'Each lesson includes practical exercises, real-world examples, and interactive challenges that help you apply concepts immediately to robotics problems.',
  },
  {
    icon: '/img/features/ai-powered.svg',
    title: 'AI-Powered Insights',
    description:
      'Access an intelligent study assistant powered by RAG technology that retrieves relevant lesson content and helps you understand complex concepts faster.',
  },
  {
    icon: '/img/features/real-world.svg',
    title: 'Real-World Robotics',
    description:
      'Learn from practical examples grounded in actual robotics systems, simulations, and deployment scenarios used in industry and research.',
  },
];

export default function Home(): JSX.Element {
  return (
    <Layout title="Physical AI & Humanoid Robotics Textbook" description="Learn to build and control the future of embodied intelligence">
      {/* Hero Section */}
      <HomepageHero
        title="Physical AI & Humanoid Robotics"
        subtitle="Learn to build and control the future of embodied intelligence"
        coverImage="/img/cover/book-cover.svg"
        ctaUrl="/docs/module-1-foundations/lesson-1-1-intro-to-physical-ai"
        ctaText="Start Learning"
      />

      {/* Features Section */}
      <FeaturesSection features={features} />

      {/* Modules Section */}
      <section className={styles.modulesSection}>
        <div className={styles.modulesContainer}>
          <h2 className={styles.modulesTitle}>Your Learning Path</h2>
          <p className={styles.modulesSubtitle}>
            Four comprehensive modules designed to take you from fundamentals to advanced applications
          </p>

          <div className={styles.modulesGrid}>
            {modules.map((module) => (
              <ModuleCard
                key={module.moduleNumber}
                moduleNumber={module.moduleNumber}
                title={module.title}
                description={module.description}
                learningGoals={module.learningGoals}
                icon={module.icon}
                firstLessonUrl={module.firstLessonUrl}
              />
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className={styles.ctaSection}>
        <div className={styles.ctaContainer}>
          <h2 className={styles.ctaTitle}>Ready to Master Physical AI?</h2>
          <p className={styles.ctaText}>
            Start with the fundamentals and progress at your own pace. Each module builds upon the previous one to give you a complete understanding of embodied AI systems.
          </p>
          <div className={styles.ctaButtons}>
            <Link to="/docs/module-1-foundations/lesson-1-1-intro-to-physical-ai" className={styles.primaryButton}>
              Begin Module 1
            </Link>
            <a
              href="https://github.com/panaversity"
              target="_blank"
              rel="noopener noreferrer"
              className={styles.secondaryButton}
            >
              View on GitHub
            </a>
          </div>
        </div>
      </section>

      {/* Footer Section */}
      <footer className={styles.footer}>
        <div className={styles.footerContent}>
          <div className={styles.footerSection}>
            <h4>About</h4>
            <p>
              A comprehensive textbook for learning Physical AI and Humanoid Robotics, designed for students and professionals.
            </p>
          </div>

          <div className={styles.footerSection}>
            <h4>Author</h4>
            <p>
              <strong>Syeda Rajda Bano</strong>
              <br />
              Student of GIAIC Q4 (Monday Evening Community)
              <br />
              <a href="https://github.com/Rajda-Hyder" target="_blank" rel="noopener noreferrer">
                GitHub Profile
              </a>
            </p>
          </div>

          <div className={styles.footerSection}>
            <h4>Community</h4>
            <p>
              Part of the{' '}
              <a href="https://github.com/panaversity" target="_blank" rel="noopener noreferrer">
                Panaversity Community
              </a>
            </p>
          </div>
        </div>

        <div className={styles.footerBottom}>
          <p>
            &copy; {new Date().getFullYear()} Syeda Rajda Bano. All rights reserved. | Built with{' '}
            <a href="https://docusaurus.io" target="_blank" rel="noopener noreferrer">
              Docusaurus v3
            </a>
          </p>
        </div>
      </footer>
    </Layout>
  );
}
