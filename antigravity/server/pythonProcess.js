import { spawn } from 'child_process';

export function getPythonCommand() {
  return process.platform === 'win32' ? 'python' : 'python3';
}

export function spawnPython(args, options) {
  return spawn(getPythonCommand(), args, options);
}

export function extractMarkedJson(stdout) {
  const match = stdout.match(/---JSON_START---([\s\S]*?)---JSON_END---/);
  return match?.[1]?.trim() || '';
}
