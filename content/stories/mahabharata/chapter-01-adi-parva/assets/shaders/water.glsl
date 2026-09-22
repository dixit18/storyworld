// Phase-2 WebGL stub: river shimmer for 2.5d scenes (adi-03, adi-06).
// Not executed by the Canvas MVP; kept versioned so the upgrade path is real.
precision mediump float;
uniform sampler2D uTex;
uniform float uTime;
uniform float uSeed;
varying vec2 vUv;

void main() {
  vec2 uv = vUv;
  uv.x += 0.008 * sin(uv.y * 28.0 + uTime * 1.6 + uSeed);
  uv.y += 0.005 * sin(uv.x * 34.0 - uTime * 1.1);
  vec3 c = texture2D(uTex, uv).rgb;
  float glint = smoothstep(0.75, 1.0, sin(uv.x * 90.0 + uTime * 2.0) * sin(uv.y * 70.0 - uTime));
  gl_FragColor = vec4(c + glint * 0.08, 1.0);
}
