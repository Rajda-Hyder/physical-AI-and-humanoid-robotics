import React from 'react';
import Link from '@docusaurus/Link';
import styles from './ModuleCard.module.css';

interface ModuleCardProps {
  moduleNumber: number;
  title: string;
  description: string;
  learningGoals: string[];
  icon: string;
  firstLessonUrl: string;
}

export default function ModuleCard({
  moduleNumber,
  title,
  description,
  learningGoals,
  icon,
  firstLessonUrl,
}: ModuleCardProps): JSX.Element {
  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <img src={icon} alt={title} className={styles.icon} />
        <h3 className={styles.title}>
          Module {moduleNumber}: {title}
        </h3>
      </div>

      <p className={styles.description}>{description}</p>

      <div className={styles.learningGoals}>
        <h4>Learning Goals:</h4>
        <ul>
          {learningGoals.map((goal, idx) => (
            <li key={idx}>{goal}</li>
          ))}
        </ul>
      </div>

      <Link to={firstLessonUrl} className={styles.startButton}>
        Start Module →
      </Link>
    </div>
  );
}
