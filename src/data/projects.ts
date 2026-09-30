// The Projects timeline, newest first. Media lives in public/projects/<slug>/.
// `draft` entries appear in `npm run dev` only, never on the live site.

export interface Project {
  slug: string;
  title: string;
  /** Groups the timeline under a year marker. */
  era: string;
  date: string;
  summary: string;
  details?: string[];
  callout?: string;
  image?: { src: string; alt: string };
  gallery?: { src: string; alt: string; caption?: string }[];
  audio?: { src: string; label: string }[];
  excerpt?: { text: string; lang?: string; caption: string };
  links?: { label: string; href: string }[];
  tags?: string[];
  draft?: boolean;
}

export const projects: Project[] = [
  {
    slug: 'website',
    title: 'This website',
    era: '2026',
    date: 'Sep 2026',
    summary: 'A 3D portrait of my head that answers questions out loud in my voice.',
    details: [
      'I turned a 25-second phone video of my head into a 3D scan, then rendered it as 165,000 black dots you can drag to rotate. The face blinks, and the jaw and lips move with speech.',
      'Ask Caleb answers questions about me. Answers come only from notes I have approved for the public, synced nightly from Google Drive into a Cloudflare database, then spoken aloud through the portrait.',
      'The Context page shares the prompt I use to turn my own messages, email, calendar, and files into a knowledge wiki an AI agent can read.',
    ],
    image: { src: '/projects/website/portrait.jpg', alt: 'The stippled 3D portrait on the home page' },
    links: [
      { label: 'Talk to the portrait', href: '/' },
      { label: 'Context', href: '/context' },
    ],
    tags: ['Three.js', 'WebGL', 'Cloudflare Workers', 'Text-to-speech'],
  },
  {
    // TODO: Caleb is sending a summary.
    slug: 'mac-productivity',
    title: 'Mac productivity tool',
    era: '2026',
    date: '2026',
    summary: 'A productivity tool I built for my Mac.',
    draft: true,
  },
  {
    slug: 'work-journal',
    title: 'Automated work journal',
    era: '2026',
    date: '2026',
    summary: 'A Claude agent that writes my work journal every evening.',
    details: [
      'Each night it pulls my Granola meeting transcripts, my Google Calendar, and the Notion pages I touched that day, then writes what I did, what I learned, and tomorrow’s priorities into Notion.',
      'It replaced 15–20 minutes of manual reflection a day.',
    ],
    tags: ['Claude', 'Scheduled tasks', 'Notion', 'Granola'],
  },
  {
    // TODO: date, functionality, and a photo of the original fuzzy orange Milo.
    slug: 'milo',
    title: 'Milo',
    era: '2026',
    date: '2026',
    summary: 'A fuzzy orange AI companion.',
    draft: true,
  },
  {
    // TODO: date and a screenshot of a scripture showing after a highlight.
    slug: 'scripture-extension',
    title: 'Scripture lookup extension',
    era: '2026',
    date: '2026',
    summary: 'My first project with Claude Code: highlight a scripture reference and the verse appears.',
    details: [
      'A Chrome extension. Highlight a reference like “John 3:16” on any web page and the full verse shows up right there.',
      'It was the first thing I built with Claude Code, and the moment I realized I could make my own software.',
    ],
    tags: ['Chrome extension', 'JavaScript', 'Claude Code'],
    draft: true,
  },
  {
    slug: 'marriott-case',
    title: 'BYU Marriott Case Competition',
    era: '2024',
    date: 'Fall 2024',
    summary: 'Won first place with a growth strategy for Skullcandy.',
    callout: '$5,000 prize',
    details: [
      'The case: grow Skullcandy beyond its core 12–24-year-old board-sports buyers without losing the loyalty of the fans it already had.',
      'Our answer was to turn the brand into a community. We pushed Skullcandy into Bluetooth speakers and gaming, widened its target demographics, and paired that with limited-edition drops, athlete and brand sponsorships, and quarterly live Sound Sessions. A pro forma P&L and balance sheet backed the plan, with a forecast of about $605M in revenue.',
      'Team: Caleb Haymore, Brayden Hancock, Avery Porter, Nathaniel Hatch, and Ian Hua.',
    ],
    // TODO: team photo at /projects/marriott-case/team.jpg, deck at /projects/marriott-case/deck.pdf.
    tags: ['Strategy', 'Financial modeling', 'Presenting'],
  },
  {
    // TODO: mission dates, 1–2 photos in Taiwan, an early voice clip, and a late clip or essay.
    slug: 'chinese',
    title: 'Learning Chinese',
    era: 'Taiwan',
    date: 'Mission',
    summary: 'I learned Mandarin from zero as a missionary in Taiwan.',
    details: [
      'Here is the progress in my own voice: a recording from my first weeks, and one from near the end.',
    ],
    tags: ['Mandarin', 'Taiwan'],
    draft: true,
  },
];

export const visibleProjects = projects.filter((project) => import.meta.env.DEV || !project.draft);
