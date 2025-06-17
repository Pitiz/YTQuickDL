function CheckBoxesChecked() {
    if (document.querySelectorAll(".control input:checked").length > 0)
        $("#download_button").css("background", "#21592473");
    else
        $("#download_button").css("background", "#231d3e73");
}

var dataLoaded = false

async function loadData() {
    const urlInput = $("#url-input").val();

    if (urlInput == "" || urlInput == null) {
        alert("Invalid URL");
        return;
    }

    $("#download_finished").html("");
    $("#loaded_values").html("");
    $("#loader").css("display", "block");

    try {
        const response = await fetch("/load", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: urlInput }),
        });

        if (!response.ok)
            throw new Error(`HTTP error! Status: ${response.status}`);

        const data = await response.json();

        draw_table(data);

        dataLoaded = true;
    } catch (error) {
        console.error("Error loading data:", error);
        alert("Failed to load data. Check the console for details.");
    }
}

function draw_table(data) {
    const tableBody = $("#table-body");
    tableBody.html(""); // Clear previous results

    data.forEach((item, index) => {
        const row = $("<tr></tr>");

        const checkboxCell = $("<td></td>");
        checkboxCell.css("display", "flex");
        checkboxCell.css("width", "auto");
        checkboxCell.css("justify-content", "center");

        const checkBoxLabel = $("<label></label>");
        checkBoxLabel.addClass("control");
        checkBoxLabel.addClass("control-checkbox");

        const controlIndicator = $("<div></div>");
        controlIndicator.addClass("control_indicator");

        const checkbox = $("<input>", {
            type: 'checkbox',
        });

        checkbox.attr("data-id", index);
        checkbox.attr("data-url", item.url);
        checkbox.attr("data-title", item.title);

        checkbox.on("change", function () {
            CheckBoxesChecked();
        });

        checkBoxLabel.append(checkbox);
        checkBoxLabel.append(controlIndicator);

        checkboxCell.append(checkBoxLabel);

        const titleCell = $("<td>").html(item.title);

        const progressCell = $("<td>", {
            id: "progress_" + index
        });

        row.append(checkboxCell);
        row.append(titleCell);
        row.append(progressCell);

        tableBody.append(row);

        $("#table-container").css("display", "block");
        $("#loader").css("display", "none");
    });

    $("#loaded_values").html("Loaded " + data.length + " videos.");
}

function getSelectedFormat() {
    const formatSelect = $("#format-select");
    return formatSelect.val();
}

async function sendDownloadRequest(urls, format) {
    try {
        const response = fetch("/download", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                urls: urls,
                format: format,
                dest_folder: $("#dest_folder").val(),
            }),
        })
            .then((response) => response.text())
            .then((data) => {
                let parsed = JSON.parse(data);
                if (parsed['status'] == "success")
                    $("#download_finished").html(parsed['message'])
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
                        if (!response.ok)
                            throw new Error("Network response was not ok");
                        return response.text();
                    })
                    .then(data => {
                        $("#progress_" + item.id).html(data);
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
    const tableBody = $("#table-body");
    const rows = $(tableBody).find("tr");

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
    const tableBody = $("#table-body");
    const rows = $(tableBody).find("tr");
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

window.onbeforeunload = function () {
    if(dataLoaded === false)
        return undefined
    return "Are you sure you want to leave? Data will be lost.";
};