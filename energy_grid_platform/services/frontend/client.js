async function runKernel() {
  const res = await fetch('/kernel', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scale: 1.0 })
  });
  const json = await res.json();
  document.getElementById('output').textContent = JSON.stringify(json, null, 2);
}
document.getElementById('run').addEventListener('click', runKernel);

