function CheckBoxesChecked() {
    if (document.querySelectorAll(".control input:checked").length > 0) {
        document.getElementById("download_button").style.background = "#21592473";
    } else {
        document.getElementById("download_button").style.background = "#231d3e73";
    }
}
async function loadData() {
    const urlInput = document.getElementById("url-input").value;

    if (urlInput == "" || urlInput == null) {
        alert("Invalid URL");
        return;
    }

    document.getElementById("download_finished").innerText = "";
    document.getElementById("loaded_values").innerText = "";

    document.getElementById("loader").style.display = "block";

    try {
        const response = await fetch("/load", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: urlInput }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();

        draw_table(data);

    } catch (error) {
        console.error("Error loading data:", error);
        alert("Failed to load data. Check the console for details.");
    }
}

function draw_table(data) {
    const tableBody = document.getElementById("table-body");
    tableBody.innerHTML = ""; // Clear previous results

    data.forEach((item, index) => {
        const row = document.createElement("tr");

        const checkboxCell = document.createElement("td");
        checkboxCell.style.display = "flex";
        checkboxCell.style.width = "auto";
        checkboxCell.style.justifyContent = "center";

        const checkBoxLabel = document.createElement("label");
        checkBoxLabel.classList.add("control");
        checkBoxLabel.classList.add("control-checkbox");

        const controlIndicator = document.createElement("div");
        controlIndicator.classList.add("control_indicator");

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.id = `item-${index}`;
        checkbox.setAttribute("data-id", index);
        checkbox.setAttribute("data-url", item.url);
        checkbox.setAttribute("data-title", item.title);
        checkbox.addEventListener("change", function () {
            CheckBoxesChecked();
        });

        checkBoxLabel.appendChild(checkbox);
        checkBoxLabel.appendChild(controlIndicator);

        checkboxCell.appendChild(checkBoxLabel);

        const titleCell = document.createElement("td");
        titleCell.textContent = item.title;

        const progressCell = document.createElement("td");
        progressCell.textContent = "";
        progressCell.id = "progress_" + index;

        row.appendChild(checkboxCell);
        row.appendChild(titleCell);
        row.appendChild(progressCell);

        tableBody.appendChild(row);

        document.getElementById("table-container").style.display = "block";
        document.getElementById("loader").style.display = "none";
    });

    document.getElementById("loaded_values").innerText = "Loaded " + data.length + " videos.";
}

function getSelectedFormat() {
    const formatSelect = document.getElementById("format-select");
    return formatSelect.value;
}

async function sendDownloadRequest(urls, format) {
    try {
        const response = fetch("/download", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                urls: urls,
                format: format,
                dest_folder: document.getElementById("dest_folder").value,
            }),
        })
            .then((response) => response.text())
            .then((data) => {
                let parsed = JSON.parse(data);
                if (parsed['status'] == "success") {
                    document.getElementById("download_finished").innerText = parsed['message']
                }
            })
            .catch((error) => {
                alert("Error:", error);
            });

        processUrlsSequentially(urls);

        const result = await response;
    } catch (error) {
        console.error("Download request failed:", error);
        alert("Failed to start download.");
    }
}

function processUrlsSequentially(urls) {
    let index = 0;

    function checkProgress(item) {
        return new Promise((resolve, reject) => {
            const interval = setInterval(() => {
                fetch("/progress/" + item.id, { method: "GET" })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error("Network response was not ok");
                        }
                        return response.text();
                    })
                    .then(data => {
                        document.getElementById("progress_" + item.id).innerText = data;
                        if (data === "100.0%" || data === "FAILED") {
                            clearInterval(interval);
                            resolve();
                        }
                    })
                    .catch(error => {
                        console.error("Fetch error:", error);
                        clearInterval(interval);
                        reject(error);
                    });
            }, 200);
        });
    }

    function processNext() {
        if (index >= urls.length) {
            console.log("All downloads complete.");
            return;
        }
        const item = urls[index];
        checkProgress(item)
            .then(() => {
                index++;
                processNext();
            })
            .catch(error => {
                console.error("Error processing item:", error);
                index++;
                processNext();
            });
    }

    processNext();
}


function selectAll() {
    const format = getSelectedFormat();
    const tableBody = document.getElementById("table-body");
    const rows = tableBody.getElementsByTagName("tr");

    if (rows.length === 0) {
        alert("No items to select.");
        return;
    }

    for (const row of rows) {
        row.querySelector('input[type="checkbox"]').checked = true;
    }

    CheckBoxesChecked();
}

function downloadSelected() {
    const format = getSelectedFormat();
    const tableBody = document.getElementById("table-body");
    const rows = tableBody.getElementsByTagName("tr");
    const list = [];

    for (const row of rows) {
        const checkbox = row.querySelector('input[type="checkbox"]');
        if (checkbox && checkbox.checked) {
            const id = checkbox.getAttribute("data-id");
            const url = checkbox.getAttribute("data-url");
            const title = checkbox.getAttribute("data-title");

            list.push({
                id: id,
                url: url,
                title: title,
            });
        }
    }

    if (list.length === 0) {
        alert("No items selected.");
        return;
    }

    sendDownloadRequest(list, format);
}

window.onbeforeunload = function() {
  return "Are you sure you want to leave? Data will be lost.";
};