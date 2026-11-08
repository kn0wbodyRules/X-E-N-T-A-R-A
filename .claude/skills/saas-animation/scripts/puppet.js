// Puppet pins for flat illustrations (like After Effects' Puppet tool): a triangle mesh over a cut-out PNG, bent by pins.
// Each pin owns a rigid move (translate + rotate + scale about the pin). Every vertex blends the pins' moves by inverse-distance
// weights, so the art bends smoothly between pins and stays put where a pin is still.
//   const P = Puppet.create(img, pins, { cols: 64 })   pins: [{ x, y }] in image pixels
//   P.draw(ctx2d, moves, x, y, scale)                   moves: per pin { dx, dy, rot, s, ox, oy } (ox/oy: pivot, default the pin)
window.Puppet = (() => {
  const VS = `#version 300 es
    in vec2 aP; in vec2 aUV; uniform vec2 uRes; out vec2 vUV;
    void main() { vUV = aUV; vec2 c = aP / uRes * 2.0 - 1.0; gl_Position = vec4(c.x, -c.y, 0.0, 1.0); }`;
  const FS = `#version 300 es
    precision highp float; in vec2 vUV; uniform sampler2D uT; out vec4 o;
    void main() { o = texture(uT, vUV); }`;
  let glc = null, gl = null, prog = null, U = {};
  function ensure(w, h) {
    if (!glc) {
      glc = document.createElement('canvas'); gl = glc.getContext('webgl2', { premultipliedAlpha: true, antialias: true, preserveDrawingBuffer: true });
      const sh = (t, s) => { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw gl.getShaderInfoLog(o); return o; };
      prog = gl.createProgram(); gl.attachShader(prog, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(prog);
      U = { res: gl.getUniformLocation(prog, 'uRes'), t: gl.getUniformLocation(prog, 'uT') };
    }
    if (glc.width !== w || glc.height !== h) { glc.width = w; glc.height = h; }
  }
  function create(img, pins, opts = {}) {
    const W = img.naturalWidth, H = img.naturalHeight, cols = opts.cols || 64, rows = Math.round(cols * H / W);
    const a = document.createElement('canvas'); a.width = cols * 4; a.height = rows * 4; const ac = a.getContext('2d'); ac.drawImage(img, 0, 0, a.width, a.height);
    const ad = ac.getImageData(0, 0, a.width, a.height).data, solid = (u, v) => ad[((Math.min(a.height - 1, Math.floor(v * a.height)) * a.width) + Math.min(a.width - 1, Math.floor(u * a.width))) * 4 + 3] > 8;
    const rest = [], uv = [];
    for (let j = 0; j <= rows; j++) for (let i = 0; i <= cols; i++) { rest.push(i / cols * W, j / rows * H); uv.push(i / cols, j / rows); }
    const idx = [];
    for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {   // keep a cell if any of it is art (checked on a 4 x 4 sample)
      let keep = false; for (let sv = 0; sv < 4 && !keep; sv++) for (let su = 0; su < 4 && !keep; su++) keep = solid((i + (su + 0.5) / 4) / cols, (j + (sv + 0.5) / 4) / rows);
      if (!keep) continue; const v = j * (cols + 1) + i; idx.push(v, v + 1, v + cols + 1, v + 1, v + cols + 2, v + cols + 1); }
    const n = rest.length / 2, P = pins.length, w = new Float32Array(n * P), pw = opts.power || 3;
    for (let k = 0; k < n; k++) { let sum = 0; for (let p = 0; p < P; p++) { const d = Math.hypot(rest[2 * k] - pins[p].x, rest[2 * k + 1] - pins[p].y) / (pins[p].r || 1); const v = 1 / Math.pow(d * d + 40, pw / 2); w[k * P + p] = v; sum += v; } for (let p = 0; p < P; p++) w[k * P + p] /= sum; }
    const pos = new Float32Array(n * 2);
    let tex = null, vao = null, pbuf = null;
    function setup() {
      tex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, tex); gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, true);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img); gl.generateMipmap(gl.TEXTURE_2D);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      vao = gl.createVertexArray(); gl.bindVertexArray(vao);
      pbuf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, pbuf); gl.bufferData(gl.ARRAY_BUFFER, pos, gl.DYNAMIC_DRAW);
      const lp = gl.getAttribLocation(prog, 'aP'); gl.enableVertexAttribArray(lp); gl.vertexAttribPointer(lp, 2, gl.FLOAT, false, 0, 0);
      const ub = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, ub); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(uv), gl.STATIC_DRAW);
      const lu = gl.getAttribLocation(prog, 'aUV'); gl.enableVertexAttribArray(lu); gl.vertexAttribPointer(lu, 2, gl.FLOAT, false, 0, 0);
      const ib = gl.createBuffer(); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, ib); gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint32Array(idx), gl.STATIC_DRAW);
    }
    function deform(moves) {   // each pin's rigid move, blended per vertex
      const M = pins.map((p, i) => { const m = moves[i] || {}, ox = m.ox ?? p.x, oy = m.oy ?? p.y, c = Math.cos(m.rot || 0) * (m.s ?? 1), s = Math.sin(m.rot || 0) * (m.s ?? 1); return [c, s, ox, oy, m.dx || 0, m.dy || 0]; });
      for (let k = 0; k < n; k++) { const x = rest[2 * k], y = rest[2 * k + 1]; let X = 0, Y = 0;
        for (let p = 0; p < P; p++) { const wt = w[k * P + p]; if (wt < 1e-5) continue; const [c, s, ox, oy, dx, dy] = M[p], rx = x - ox, ry = y - oy; X += wt * (ox + c * rx - s * ry + dx); Y += wt * (oy + s * rx + c * ry + dy); }
        pos[2 * k] = X; pos[2 * k + 1] = Y; }
    }
    function draw(ctx, moves, x, y, scale, cw, ch) {   // into a 2D canvas, image pixel (0,0) at (x, y), cw x ch the target's pixel size
      ensure(cw, ch); if (!tex) setup(); deform(moves);
      gl.viewport(0, 0, cw, ch); gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT); gl.useProgram(prog);
      for (let k = 0; k < n; k++) { pos[2 * k] = x + pos[2 * k] * scale; pos[2 * k + 1] = y + pos[2 * k + 1] * scale; }
      gl.bindVertexArray(vao); gl.bindBuffer(gl.ARRAY_BUFFER, pbuf); gl.bufferSubData(gl.ARRAY_BUFFER, 0, pos);
      gl.uniform2f(U.res, cw, ch); gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, tex); gl.uniform1i(U.t, 0);
      gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA); gl.drawElements(gl.TRIANGLES, idx.length, gl.UNSIGNED_INT, 0);
      ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.drawImage(glc, 0, 0); ctx.restore();
    }
    return { draw, pins, W, H, tris: idx.length / 3 };
  }
  return { create };
})();
