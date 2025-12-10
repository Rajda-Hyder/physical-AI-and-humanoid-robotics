import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import BrowserOnly from '@docusaurus/BrowserOnly';
import { useAuth } from '../contexts/AuthContext';
import styles from './dashboard.module.css';

const DashboardPageContent: React.FC = () => {
  const { user, loading, signOut } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && !user) {
      navigate('/login');
    }
  }, [user, loading, navigate]);

  const handleSignOut = async () => {
    await signOut();
    navigate('/');
  };

  if (loading) {
    return (
      <Layout title="Dashboard - Physical AI & Humanoid Robotics">
        <div className={styles.dashboardContainer}>
          <div className={styles.loadingState}>
            <div className={styles.spinner} />
            <p>Loading...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <Layout title="Dashboard - Physical AI & Humanoid Robotics">
      <div className={styles.dashboardContainer}>
        <div className={styles.dashboardHeader}>
          <div className={styles.userInfo}>
            <h1>Welcome, {user.displayName || user.email}</h1>
            <p className={styles.email}>{user.email}</p>
          </div>
          <button onClick={handleSignOut} className={styles.signOutButton}>
            Sign Out
          </button>
        </div>

        <div className={styles.dashboardContent}>
          <section className={styles.section}>
            <h2>Your Learning Journey</h2>
            <div className={styles.modulesGrid}>
              <div className={styles.moduleCard}>
                <h3>Module 1: Foundations</h3>
                <p>
                  Explore the fundamentals of physical AI and embodied
                  intelligence
                </p>
                <Link to="/docs/module-1-foundations/lesson-1-1-intro-to-physical-ai">
                  Continue Learning →
                </Link>
              </div>

              <div className={styles.moduleCard}>
                <h3>Module 2: Embodied Robotics</h3>
                <p>
                  Learn about sensors, control systems, and physical engagement
                </p>
                <Link to="/docs/module-2-embodied-robotics/lesson-2-1-sensing-taking-action">
                  Continue Learning →
                </Link>
              </div>

              <div className={styles.moduleCard}>
                <h3>Module 3: Humanoid AI Agents</h3>
                <p>
                  Design and understand humanoid robots and autonomous agents
                </p>
                <Link to="/docs/module-3-humanoid-ai-agents/lesson-3-1-building-human-like-robots">
                  Continue Learning →
                </Link>
              </div>

              <div className={styles.moduleCard}>
                <h3>Module 4: Applied AI-Native Systems</h3>
                <p>
                  Master deployment, personalization, and real-world
                  applications
                </p>
                <Link to="/docs/module-4-applied-ai-native/lesson-4-1-simulation-to-reality">
                  Continue Learning →
                </Link>
              </div>
            </div>
          </section>

          <section className={styles.section}>
            <h2>Quick Stats</h2>
            <div className={styles.statsGrid}>
              <div className={styles.statCard}>
                <div className={styles.statNumber}>4</div>
                <p>Modules Available</p>
              </div>
              <div className={styles.statCard}>
                <div className={styles.statNumber}>12</div>
                <p>Comprehensive Lessons</p>
              </div>
              <div className={styles.statCard}>
                <div className={styles.statNumber}>27+</div>
                <p>Hands-On Exercises</p>
              </div>
              <div className={styles.statCard}>
                <div className={styles.statNumber}>10k+</div>
                <p>Words of Content</p>
              </div>
            </div>
          </section>

          <section className={styles.section}>
            <h2>Featured Resources</h2>
            <div className={styles.resourcesGrid}>
              <div className={styles.resourceCard}>
                <h4>RAG Chatbot</h4>
                <p>
                  Use our AI-powered study assistant to ask questions about the
                  textbook content
                </p>
              </div>
              <div className={styles.resourceCard}>
                <h4>Interactive Exercises</h4>
                <p>
                  Test your understanding with hands-on projects and design
                  challenges
                </p>
              </div>
              <div className={styles.resourceCard}>
                <h4>Real-World Examples</h4>
                <p>
                  Learn from industry examples and cutting-edge robotics
                  applications
                </p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </Layout>
  );
};

const DashboardPage: React.FC = () => (
  <BrowserOnly fallback={<div>Loading...</div>}>
    {() => <DashboardPageContent />}
  </BrowserOnly>
);

export default DashboardPage;
