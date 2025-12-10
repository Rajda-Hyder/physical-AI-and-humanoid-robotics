import React from 'react';
import Link from '@docusaurus/Link';
import styles from './HomepageHero.module.css';

interface HomepageHeroProps {
  title: string;
  subtitle: string;
  coverImage: string;
  ctaUrl: string;
  ctaText?: string;
}

export default function HomepageHero({
  title,
  subtitle,
  coverImage,
  ctaUrl,
  ctaText = 'Start Learning',
}: HomepageHeroProps): JSX.Element {
  return (
    <div className={styles.heroContainer}>
      <div className={styles.heroContent}>
        <div className={styles.heroText}>
          <h1 className={styles.title}>{title}</h1>
          <p className={styles.subtitle}>{subtitle}</p>
          <Link className={styles.ctaButton} to={ctaUrl}>
            {ctaText}
          </Link>
        </div>
        <div className={styles.heroImage}>
          <img src={coverImage} alt={title} />
        </div>
      </div>
    </div>
  );
}
