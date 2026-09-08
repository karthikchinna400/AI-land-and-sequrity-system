// ==========================================
// AI LANDSLIDE RISK MONITORING SYSTEM
// ==========================================

// Initial sensor values
let sensorData = {
    rainfall: 72,
    soil: 68,
    slope: 42,
    water: 54,
    cracks: 35
};


// ==========================================
// GENERATE AUTOMATIC SENSOR DATA
// ==========================================

function generateSensorData() {

    // Small changes to make the dashboard look live
    sensorData.rainfall = randomChange(sensorData.rainfall, 5, 0, 100);

    sensorData.soil = randomChange(sensorData.soil, 4, 0, 100);

    sensorData.slope = randomChange(sensorData.slope, 2, 5, 90);

    sensorData.water = randomChange(sensorData.water, 4, 0, 100);

    sensorData.cracks = randomChange(sensorData.cracks, 5, 0, 100);

    updateWebsite();
}


// ==========================================
// RANDOM SENSOR CHANGE
// ==========================================

function randomChange(value, change, min, max) {

    let newValue =
        value + (Math.random() * change * 2 - change);

    return Math.min(
        max,
        Math.max(min, Math.round(newValue))
    );
}


// ==========================================
// AI SENSOR FUSION
// ==========================================

function calculateRisk() {

    /*
        AI Sensor Fusion Weights

        Rainfall       = 30%
        Soil Moisture  = 25%
        Slope          = 20%
        Water Level    = 10%
        Ground Cracks  = 15%
    */

    let risk =
        sensorData.rainfall * 0.30 +
        sensorData.soil * 0.25 +
        sensorData.slope * 0.20 +
        sensorData.water * 0.10 +
        sensorData.cracks * 0.15;

    return Math.round(risk);
}


// ==========================================
// UPDATE WEBSITE
// ==========================================

function updateWebsite() {

    // -----------------------------
    // Sensor values
    // -----------------------------

    document.getElementById("rainfall").innerText =
        sensorData.rainfall + "%";

    document.getElementById("soil").innerText =
        sensorData.soil + "%";

    document.getElementById("slope").innerText =
        sensorData.slope + "°";

    document.getElementById("water").innerText =
        sensorData.water + "%";

    document.getElementById("cracks").innerText =
        sensorData.cracks + "%";


    // -----------------------------
    // Progress bars
    // -----------------------------

    document.getElementById("rainBar").style.width =
        sensorData.rainfall + "%";

    document.getElementById("soilBar").style.width =
        sensorData.soil + "%";

    // Convert slope 5–90° to percentage
    let slopePercentage =
        ((sensorData.slope - 5) / 85) * 100;

    document.getElementById("slopeBar").style.width =
        slopePercentage + "%";

    document.getElementById("waterBar").style.width =
        sensorData.water + "%";

    document.getElementById("crackBar").style.width =
        sensorData.cracks + "%";


    // -----------------------------
    // AI Risk
    // -----------------------------

    let risk = calculateRisk();

    document.getElementById("risk").innerText =
        risk + "%";


    // -----------------------------
    // Risk level
    // -----------------------------

    let riskLevel =
        document.getElementById("riskLevel");

    let alert =
        document.getElementById("alert");


    if (risk >= 65) {

        riskLevel.innerText =
            "HIGH RISK";

        alert.innerText =
            "🚨 LANDSLIDE WARNING — Immediate monitoring required.";

        riskLevel.style.color = "#ff4d4d";

        document.getElementById("risk")
            .style.color = "#ff4d4d";

    }

    else if (risk >= 35) {

        riskLevel.innerText =
            "MEDIUM RISK";

        alert.innerText =
            "⚠️ WARNING — Monitor the area carefully.";

        riskLevel.style.color = "#f5a623";

        document.getElementById("risk")
            .style.color = "#f5a623";

    }

    else {

        riskLevel.innerText =
            "LOW RISK";

        alert.innerText =
            "✅ Area currently appears relatively safe.";

        riskLevel.style.color = "#36d399";

        document.getElementById("risk")
            .style.color = "#36d399";
    }
}


// ==========================================
// CAMERA FUNCTION
// ==========================================

function startCamera() {

    alert(
        "📷 Camera monitoring started!\n\n" +
        "AI camera will analyze the terrain " +
        "for visible ground cracks."
    );

}


// ==========================================
// INITIAL WEBSITE LOAD
// ==========================================

updateWebsite();


// ==========================================
// AUTOMATIC MONITORING
// Updates every 3 seconds
// ==========================================

setInterval(function () {

    generateSensorData();

}, 3000);