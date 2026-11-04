// Bundled fallback so the studio / render always has a valid payload to draw
// even when public/assets/render_payload.json is missing. This is the Braess's
// Paradox verification mock (requirement 6.1).

import braess from "./mock/render_payload.json";
import type { VideoRenderPayload } from "./types/schema";

export const FALLBACK_PAYLOAD = braess as unknown as VideoRenderPayload;
