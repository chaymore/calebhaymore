export type PortraitView = 'dots' | 'ascii';

/** Glyphs from empty to full ink. The first is a space so bare paper stays blank. */
export const ASCII_RAMP = ' .:-=+*#%@';

/** A ?view= link wins, then the visitor's last choice, then dots. */
export function resolveView(search: string, stored: string | null): PortraitView {
  const asked = new URLSearchParams(search).get('view');
  if (asked === 'ascii' || asked === 'dots') return asked;
  return stored === 'ascii' ? 'ascii' : 'dots';
}

/** Character cell in device pixels: about 85 rows down the stage, 7–12 CSS px tall, monospace 0.6 aspect. */
export function asciiCell(cssHeight: number, pixelRatio: number): { width: number; height: number } {
  const height = Math.max(7, Math.min(12, cssHeight / 85)) * pixelRatio;
  return { width: Math.round(height * 0.6), height: Math.round(height) };
}
