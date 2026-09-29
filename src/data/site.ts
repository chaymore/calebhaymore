export const site = {
  name: 'Caleb Haymore',
  tagline: 'Finance, law, and systems thinking.',
  intro:
    'Finance student at BYU interested in the touchpoint between finance and law. Find me on the tennis court or reading a sci-fi novel.',
  email: 'calebhaymore@gmail.com',
  socialLinks: [
    { label: 'GitHub', href: 'https://github.com/chaymore' },
    { label: 'LinkedIn', href: 'https://www.linkedin.com/in/caleb-haymore/' },
    { label: 'Instagram', href: 'https://www.instagram.com/caleb_haymore/' },
  ],
};

export const pageLinks = [
  { href: '/', label: 'Home' },
  { href: '/about', label: 'About' },
  { href: '/context', label: 'Context' },
  { href: '/competitions', label: 'Competitions' },
  { href: '/research', label: 'Research' },
  { href: '/writing', label: 'Writing' },
  { href: '/projects', label: 'Projects' },
  { href: '/contact', label: 'Contact' },
];

export const competitions = [
  {
    name: 'Marriott Case Competition',
    description: 'Add a description of the case, your role, and outcomes here.',
    year: '2025',
    placement: '1st Place',
  },
  {
    name: 'Ballard Center Case Competition',
    description: 'Add a description of the case, your role, and outcomes here.',
    year: '2025',
    placement: '3rd Place',
  },
  {
    name: 'Global Business Center Case Competition',
    description: 'Add a description of the case, your role, and outcomes here.',
    year: '2026',
    placement: '',
  },
];

export const research = [
  {
    title: 'Paper Title',
    abstract: 'Add a brief abstract or summary of your research here.',
    href: '',
  },
];

export const essays = [
  {
    title: 'Essay Title',
    date: 'Month Year',
    summary: 'Add a one or two sentence summary of the essay here.',
    href: '',
  },
];

// Newest first. `date` is shown on the timeline; `href` links to the live project.
export const projects: {
  title: string;
  date: string;
  description: string;
  tags: string[];
  repo?: string;
  href?: string;
}[] = [
  {
    title: 'Context',
    date: 'Sep 2026',
    description:
      'A public guide to collecting the context that already describes you (messages, email, calendar, files) and compiling it into a private knowledge wiki an AI agent can read. One prompt does the compiling.',
    tags: ['Prompt design', 'Knowledge wiki'],
    href: '/context',
  },
  {
    title: 'Ask Caleb',
    date: 'Sep 2026',
    description:
      'A digital version of me that answers questions out loud. Answers are grounded only in notes I have approved for the public, synced nightly from Google Drive into a Cloudflare database, and spoken through the 3D portrait with a lip-synced mouth.',
    tags: ['Cloudflare Workers', 'D1', 'OpenRouter', 'Text-to-speech'],
    href: '/',
  },
  {
    title: '3D stippled portrait',
    date: 'Sep 2026',
    description:
      'I turned a 25-second phone video of my head into a 3D scan, then rendered it as 165,000 black dots you can drag to rotate. The face blinks, and the jaw and lips move with speech.',
    tags: ['Three.js', 'WebGL shaders', 'Photogrammetry'],
    href: '/',
  },
  {
    title: 'Life hub',
    date: 'Aug 2026',
    description:
      'A private, PIN-gated workspace built as a calm animated meadow, with tiles for the things I check every day.',
    tags: ['Canvas animation', 'Personal tools'],
  },
  {
    title: 'Automated end-of-day work journal',
    date: '2026',
    description:
      'A scheduled Claude agent that writes my work journal every evening. It pulls my Granola meeting transcripts, Google Calendar, and the Notion pages I touched that day, then writes what I did, what I learned, and tomorrow’s priorities into Notion. It replaced 15–20 minutes of manual reflection a day.',
    tags: ['Claude Desktop', 'Scheduled tasks', 'Granola', 'Notion', 'Google Calendar'],
  },
  {
    title: 'This website',
    date: 'Mar 2026',
    description:
      'Built from scratch with Astro and deployed on GitHub Pages. Earlier versions had a terminal you could type into and a live three-body gravity simulation.',
    tags: ['Astro', 'TypeScript', 'GitHub Pages'],
  },
];
