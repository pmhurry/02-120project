import { build } from 'esbuild';
import { mkdir, copyFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('.', import.meta.url));
const output = new URL('../frontend_dist/', import.meta.url);
await mkdir(output, {recursive: true});
await build({
  absWorkingDir: root,
  entryPoints: ['src/main.jsx'],
  outdir: fileURLToPath(output),
  bundle: true,
  minify: true,
  jsx: 'automatic',
  define: {'process.env.NODE_ENV': '"production"'},
});
await copyFile(new URL('index.html', import.meta.url), new URL('index.html', output));
await Promise.all(
  ['heldout_evaluation.json', 'heldout_predictions.csv', 'heldout_plot.svg'].map(name =>
    copyFile(new URL('../results/compound_activity/' + name, import.meta.url), new URL(name, output))
  )
);
