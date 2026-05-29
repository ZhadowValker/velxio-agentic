/**
 * SoundMind-local custom elements.
 *
 * These are wokwi-style web components that live IN this project rather
 * than in the upstream `@wokwi/elements` package — useful when we don't
 * have push access to wokwi/wokwi-elements but still need to ship new
 * parts. SoundMind-originals use the `soundmind-` prefix (e.g.
 * `<soundmind-capacitor-electrolytic>`); local fallbacks for upstream names
 * (e.g. `<wokwi-capacitor>`, `<wokwi-inductor>`) are guarded against
 * double-registration so they only kick in if `@wokwi/elements` isn't loaded.
 *
 * Side-effect import: each module calls `customElements.define(...)` at
 * load time (guarded against double-registration), so a single
 * `import './soundmind-elements';` is enough to make the tags resolvable.
 */

import './capacitor-element';
import './capacitor-electrolytic-element';
import './inductor-element';

export { CapacitorElement } from './capacitor-element';
export { CapacitorElectrolyticElement } from './capacitor-electrolytic-element';
export { InductorElement } from './inductor-element';
