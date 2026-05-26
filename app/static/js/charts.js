function lineChart(id, label, labels, values, color, extraDatasets = []) {
  const element = document.getElementById(id);
  if (!element) return;
  if (!labels.length || values.every((value) => value === null || value === 0)) return;

  new Chart(element, {
    type: "line",
    data: {
      labels,
      datasets: [{
        label,
        data: values,
        borderColor: color,
        backgroundColor: color + "22",
        tension: 0.25,
        fill: true
      }, ...extraDatasets]
    },
    options: {
      maintainAspectRatio: false,
      responsive: true,
      plugins: { legend: { display: true } },
      scales: { y: { beginAtZero: false } }
    }
  });
}

function barChart(id, label, labels, values, color) {
  const element = document.getElementById(id);
  if (!element) return;
  if (!labels.length || values.every((value) => value === null || value === 0)) return;

  new Chart(element, {
    type: "bar",
    data: {
      labels,
      datasets: [{ label, data: values, backgroundColor: color }]
    },
    options: {
      maintainAspectRatio: false,
      responsive: true
    }
  });
}

function macroChart(id, data) {
  const element = document.getElementById(id);
  if (!element) return;
  const hasValues = [...data.protein, ...data.carbs, ...data.fat].some((value) => value > 0);
  if (!data.labels.length || !hasValues) return;

  new Chart(element, {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [
        { label: "Proteina", data: data.protein, backgroundColor: "#2f855a" },
        { label: "Carboidratos", data: data.carbs, backgroundColor: "#3182ce" },
        { label: "Gorduras", data: data.fat, backgroundColor: "#d69e2e" }
      ]
    },
    options: {
      maintainAspectRatio: false,
      responsive: true,
      scales: {
        x: { stacked: true },
        y: { stacked: true }
      }
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const data = window.NUTRITRACK_CHART_DATA;
  if (!data) return;

  lineChart(
    "weightChart",
    "Evolucao do peso",
    data.weight.labels,
    data.weight.values,
    "#2f855a",
    [{
      label: "Media movel",
      data: data.weight.movingAverage,
      borderColor: "#d69e2e",
      backgroundColor: "#d69e2e22",
      borderDash: [6, 4],
      tension: 0.25,
      fill: false
    }]
  );
  lineChart("waistChart", "Evolucao da cintura", data.waist.labels, data.waist.values, "#3182ce");
  barChart("calorieChart", "Calorias por dia", data.calories.labels, data.calories.values, "#38a169");
  macroChart("macroChart", data.macros);
});
