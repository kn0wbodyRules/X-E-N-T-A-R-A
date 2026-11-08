// Tiny WebGL2 3D stage for the spec ads: flat panels (textures drawn with normal 2D canvas code, so UI stays sharp)
// placed in 3D and seen through a perspective camera, with fog, depth of field (mip bias), and a glossy floor reflection.
// World units ~ screen px when the camera is ~1600 from the subject at fov 38. y is up.
window.GL3D = (function () {
  const M = {   // column-major mat4 helpers
    mul(a, b) { const o = new Float32Array(16); for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) { let s = 0; for (let k = 0; k < 4; k++) s += a[k * 4 + r] * b[c * 4 + k]; o[c * 4 + r] = s; } return o; },
    persp(fov, asp, n, f) { const t = 1 / Math.tan(fov / 2), o = new Float32Array(16); o[0] = t / asp; o[5] = t; o[10] = (f + n) / (n - f); o[11] = -1; o[14] = 2 * f * n / (n - f); return o; },
    look(e, c, up) { const z = norm(sub(e, c)), x = norm(cross(up, z)), y = cross(z, x);
      return new Float32Array([x[0], y[0], z[0], 0, x[1], y[1], z[1], 0, x[2], y[2], z[2], 0, -dot(x, e), -dot(y, e), -dot(z, e), 1]); },
    model(p, r, s) {   // translate * rotY * rotX * rotZ * scale
      const [rx, ry, rz] = r, cx = Math.cos(rx), sx = Math.sin(rx), cy = Math.cos(ry), sy = Math.sin(ry), cz = Math.cos(rz), sz = Math.sin(rz);
      const Ry = [cy, 0, -sy, 0, 0, 1, 0, 0, sy, 0, cy, 0, 0, 0, 0, 1], Rx = [1, 0, 0, 0, 0, cx, sx, 0, 0, -sx, cx, 0, 0, 0, 0, 1], Rz = [cz, sz, 0, 0, -sz, cz, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
      let m = M.mul(M.mul(Ry, Rx), Rz); m = M.mul([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, p[0], p[1], p[2], 1], m); return M.mul(m, [s, 0, 0, 0, 0, s, 0, 0, 0, 0, s, 0, 0, 0, 0, 1]);
    },
  };
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]], norm = a => { const l = Math.hypot(...a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };

  function create(width, height) {
    const cv = document.createElement('canvas'); cv.width = width; cv.height = height;
    const gl = cv.getContext('webgl2', { premultipliedAlpha: true, alpha: true, antialias: true, preserveDrawingBuffer: true });
    const vs = `#version 300 es
      in vec2 aP; uniform mat4 uVP, uM; uniform vec2 uS; out vec2 vUV; out vec3 vW;
      void main(){ vec4 w = uM * vec4((aP.x - 0.5) * uS.x, (0.5 - aP.y) * uS.y, 0.0, 1.0); vW = w.xyz; vUV = aP; gl_Position = uVP * w; }`;
    const fs = `#version 300 es
      precision highp float; in vec2 vUV; in vec3 vW; uniform sampler2D uT; uniform float uA, uB, uL, uFy, uRef, uFn, uFf, uSh, uShP; uniform vec3 uC, uFc; out vec4 o;
      void main(){ vec4 c = texture(uT, vUV, uB); c.rgb *= uL; c.rgb += vec3(uSh * max(0.0, 1.0 - abs(vUV.x * 0.65 + vUV.y * 0.35 - uShP) / 0.2)) * c.a;   // optional key-light sheen band
        float f = clamp((distance(vW, uC) - uFn) / (uFf - uFn), 0.0, 1.0); c.rgb = mix(c.rgb, uFc * c.a, f * 0.9);
        float a = uA; if (uRef > 0.5) { a *= 0.2 * exp(-max(0.0, uFy - vW.y) / 160.0); }
        o = c * a; }`;
    const sh = (t, s) => { const x = gl.createShader(t); gl.shaderSource(x, s); gl.compileShader(x); if (!gl.getShaderParameter(x, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(x)); return x; };
    const pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, fs)); gl.linkProgram(pr); gl.useProgram(pr);
    const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([0, 0, 1, 0, 0, 1, 1, 1]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(pr, 'aP'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    const U = {}; ['uVP', 'uM', 'uS', 'uT', 'uA', 'uB', 'uL', 'uFy', 'uRef', 'uFn', 'uFf', 'uC', 'uFc', 'uSh', 'uShP'].forEach(n => U[n] = gl.getUniformLocation(pr, n));
    const aniso = gl.getExtension('EXT_texture_filter_anisotropic');
    gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA); gl.disable(gl.DEPTH_TEST); gl.disable(gl.CULL_FACE);

    function texture(src) {   // src: a 2D canvas (or image); call .update() after redrawing it
      const t = gl.createTexture(), o = { t, src, update() {
        gl.bindTexture(gl.TEXTURE_2D, t); gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, true);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, src); gl.generateMipmap(gl.TEXTURE_2D);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        if (aniso) gl.texParameterf(gl.TEXTURE_2D, aniso.TEXTURE_MAX_ANISOTROPY_EXT, 8); } };
      o.update(); return o;
    }
    // panels: [{tex, w, h, pos:[x,y,z], rot:[rx,ry,rz], scale, alpha, light, reflect, bias, blur, sheen (0..1 highlight band), sheenPos (0..1 across the panel)}]
    // opts: {eye, target, up?, fov (deg), focus (distance), aperture (blur per unit defocus), fog:{near,far,color:[r,g,b] 0..1}, floorY}
    function render(panels, opts) {
      gl.viewport(0, 0, cv.width, cv.height); gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
      const VP = M.mul(M.persp(opts.fov * Math.PI / 180, cv.width / cv.height, 10, 40000), M.look(opts.eye, opts.target, opts.up || [0, 1, 0]));
      gl.uniformMatrix4fv(U.uVP, false, VP); gl.uniform3fv(U.uC, opts.eye); const fog = opts.fog || { near: 1e5, far: 2e5, color: [0, 0, 0] };
      gl.uniform1f(U.uFn, fog.near); gl.uniform1f(U.uFf, fog.far); gl.uniform3fv(U.uFc, fog.color); gl.uniform1f(U.uFy, opts.floorY ?? -1e6);
      const fwd = norm(sub(opts.target, opts.eye));   // sort by depth along the view (not straight-line distance) so layered panels stack correctly
      const list = panels.filter(p => p && p.tex && (p.alpha ?? 1) > 0.002).map(p => { const z = dot(sub(p.pos, opts.eye), fwd); return { p, z, d: z - (p.bias || 0) }; }).sort((a, b) => b.d - a.d);   // d sorts (bias nudges order); z is the real depth, used for focus blur
      const draw = (p, d, mirror) => {
        let m = M.model(p.pos, p.rot || [0, 0, 0], p.scale ?? 1);
        if (mirror) { const fy = opts.floorY; m = M.mul([1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 1, 0, 0, 2 * fy, 0, 1], m); }
        const blur = Math.min(7, (p.blur ?? 0) + (opts.aperture || 0) * Math.abs(d - (opts.focus || d)) / Math.max(1, opts.focus || d));
        gl.uniformMatrix4fv(U.uM, false, m); gl.uniform2f(U.uS, p.w, p.h); gl.uniform1f(U.uA, p.alpha ?? 1); gl.uniform1f(U.uB, blur + (mirror ? 1.5 : 0));
        gl.uniform1f(U.uL, p.light ?? 1); gl.uniform1f(U.uRef, mirror ? 1 : 0); gl.uniform1f(U.uSh, mirror ? 0 : (p.sheen || 0)); gl.uniform1f(U.uShP, p.sheenPos ?? 0.5);
        gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, p.tex.t); gl.uniform1i(U.uT, 0); gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      };
      (opts.ground || []).forEach(p => { if (p && p.tex && (p.alpha ?? 1) > 0.002) draw(p, opts.focus || 1, false); });   // opts.ground: floor + contact shadows, drawn first, unsorted, in focus
      if (opts.floorY != null) list.forEach(({ p, z }) => { if (p.reflect !== false) draw(p, z, true); });
      list.forEach(({ p, z }) => draw(p, z, false));
      return cv;
    }
    function project(pt, opts) {   // world point -> screen px (0..width), for screen-space extras
      const VP = M.mul(M.persp(opts.fov * Math.PI / 180, cv.width / cv.height, 10, 40000), M.look(opts.eye, opts.target, opts.up || [0, 1, 0]));
      const x = VP[0] * pt[0] + VP[4] * pt[1] + VP[8] * pt[2] + VP[12], y = VP[1] * pt[0] + VP[5] * pt[1] + VP[9] * pt[2] + VP[13], w = VP[3] * pt[0] + VP[7] * pt[1] + VP[11] * pt[2] + VP[15];
      return [(x / w * 0.5 + 0.5) * cv.width, (0.5 - y / w * 0.5) * cv.height];
    }
    return { gl, canvas: cv, texture, render, project };
  }
  return { create };
})();
