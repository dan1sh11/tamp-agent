const input = document.querySelector('#instruction');
const execute = document.querySelector('#execute');
const status = document.querySelector('#status');
const error = document.querySelector('#error');
const nli = document.querySelector('#nli');
const plan = document.querySelector('#plan');
const pddl = document.querySelector('#pddl');
const execution = document.querySelector('#execution');

document.querySelectorAll('[data-command]').forEach((button) => {
  button.addEventListener('click', () => { input.value = button.dataset.command; input.focus(); });
});

async function checkHealth() {
  try {
    const r = await fetch('/health');
    const data = await r.json();
    status.textContent = data.status === 'ok' ? 'ONLINE' : 'OFFLINE';
    status.className = `status ${data.status === 'ok' ? 'online' : 'offline'}`;
  } catch {
    status.textContent = 'OFFLINE';
    status.className = 'status offline';
  }
}

execute.addEventListener('click', async () => {
  error.textContent = '';
  if (!input.value.trim()) { error.textContent = 'Enter a robot instruction.'; return; }
  execute.disabled = true;
  execute.textContent = 'PLANNING...';
  nli.textContent = 'Processing...'; plan.textContent = 'Planning...'; pddl.textContent = 'Generating PDDL...';
  try {
    const response = await fetch('/api/plan', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({instruction: input.value})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Task failed');
    nli.textContent = JSON.stringify(data.instruction, null, 2);
    plan.textContent = data.plan;
    pddl.textContent = data.problem;
    execution.textContent = `${data.execution}\n\nActions:\n${data.actions.map((a, i) => `${i + 1}. ${a.type} ${JSON.stringify(a.parameters)}`).join('\n')}`;
  } catch (e) {
    error.textContent = e.message;
    nli.textContent = 'No result'; plan.textContent = 'No plan'; pddl.textContent = 'No problem';
  } finally {
    execute.disabled = false;
    execute.textContent = 'PLAN TASK';
  }
});

checkHealth();
