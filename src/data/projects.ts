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
    slug: 'nightlock',
    title: 'NightLock',
    era: '2026',
    date: 'Sep 2026',
    summary: 'A Mac website blocker I can’t talk myself out of.',
    details: [
      'NightLock is a native macOS app that limits the sites that eat my time. Instagram gets one 30-minute window a day. X is open during work hours, gets 10 minutes in the evening, and is blocked overnight. Everything else on the list stays blocked.',
      'A system-level background service enforces the rules, so quitting the app changes nothing. There is no quit button and no snooze, and changing the schedule takes a recovery key that is deliberately hard to reach.',
    ],
    image: { src: '/projects/nightlock/block-page.png', alt: 'NightLock’s block page: “NightLock is on. x.com is unavailable. Today’s 10-minute allowance has been used.”' },
    tags: ['Swift', 'macOS', 'Menu bar app'],
  },
  {
    // TODO: confirm Caleb wants this entry, and its date.
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
    draft: true,
  },
  {
    slug: 'milo',
    title: 'Milo',
    era: '2026',
    date: 'Apr 2026',
    summary: 'A desktop buddy that floats over everything on my Mac.',
    details: [
      'Milo is a small animated character who lives on top of every window and every desktop. You can drag him anywhere, his eyes blink and follow your cursor, and a double-click opens a chat drawer where he answers with AI.',
      'Option+B hides or shows him. He also has a bedtime mode that sends YouTube, X, Reddit, and Facebook to a funny block page between 11 PM and 6 AM.',
      'Milo was my own idea from the start. He began as a fuzzy orange character and has since become the simple black-and-white stick figure he is today.',
    ],
    image: { src: '/projects/milo/milo.png', alt: 'Milo today: a black-and-white stick figure with a small chat bubble' },
    tags: ['Swift', 'macOS', 'AI chat'],
  },
  {
    slug: 'scripture-extension',
    title: 'Scripture Highlighter',
    era: '2026',
    date: 'Mar 2026',
    summary: 'My first project with Claude Code: scripture references on any web page turn into verses.',
    details: [
      'A Chrome extension that finds scripture references on any web page, like “John 3:16” or “1 Cor 15”, and shows the verse in a small card when you hover over it.',
      'It understands hundreds of abbreviations, switches between the King James and World English translations, and steps to the previous or next verse. The whole Bible ships inside the extension, so it works offline.',
      'It was the first thing I built with Claude Code.',
    ],
    image: { src: '/projects/scripture-extension/card.png', alt: 'The extension’s verse card showing Proverbs 3:5–6 in the King James Version, with Prev and Next buttons' },
    tags: ['Chrome extension', 'JavaScript', 'Claude Code'],
  },
  {
    slug: 'marriott-case',
    title: 'BYU Marriott Case Competition',
    era: '2025',
    date: 'Oct 2025',
    summary: 'Won first place with a go-to-market strategy for Adminify, an AI-powered CRM startup.',
    callout: '$5,000 prize',
    details: [
      'The case: Adminify had won over 1,000 small businesses since 2022, but its bigger opportunity was multi-location enterprise customers, who were worth about 2.5 times as much over their lifetime.',
      'Our answer was to partner with Housecall Pro to take over Adminify’s small-business customers with guaranteed continued service, freeing Adminify to go after enterprise clients. We backed it with a revenue-sharing model, a refreshed brand and product roadmap, a new LTV-to-CAC model (8.4 to 1), an enterprise platform fee to meet the Rule of 40, and new KPIs for tracking rollouts.',
      'Team: Luke Stacey, Dallin Christensen, Peter Hyde, Caleb Haymore, and Josh Christensen.',
    ],
    image: { src: '/projects/marriott-case/team.jpg', alt: 'Caleb and his four teammates holding the $5,000 first-place check from the BYU Marriott Case Competition, October 17, 2025' },
    // TODO: deck at /projects/marriott-case/deck.pdf.
    tags: ['Strategy', 'Financial modeling', 'Presenting'],
  },
  {
    // TODO: 1–2 photos in Taiwan, and the audio clips (see audio below).
    slug: 'chinese',
    title: 'Learning Chinese',
    era: '2022',
    date: '2022–2024',
    summary: 'Two years speaking Mandarin every day as a missionary in Taichung, Taiwan.',
    details: [
      'Here is the progress in my own voice and my own writing: a recording from my second week in Taiwan, and an essay I wrote in Chinese at the end of the two years.',
    ],
    // audio: [{ src: '/projects/chinese/week-2.mp3', label: 'Week 2 in Taiwan' }],
    excerpt: {
      lang: 'zh-Hant',
      text: '我最大的改變\n更有自信\n比較會管理和有效的利用時間\n我更能夠去愛身邊的人\n更快樂\n\n這些祝福和改變不是因傳教而來的，而是因為我在這兩年有盡力奉行耶穌基督的福音。',
      caption:
        'From “傳教的心得” (What I learned as a missionary), written at the end of my mission. My biggest changes: more confident, better with my time, better at loving the people around me, and happier. These blessings didn’t come from the mission itself, but from two years of doing my best to live the gospel of Jesus Christ.',
    },
    tags: ['Mandarin', 'Taiwan'],
    draft: true,
  },
];

export const visibleProjects = projects.filter((project) => import.meta.env.DEV || !project.draft);
