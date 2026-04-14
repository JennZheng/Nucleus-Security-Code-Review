let display = document.getElementById("display");

function press(value) {
    if (value === "AC") {
        display.value = "0";
    } 
    else if (value === "+/-") {
        display.value = (parseFloat(display.value) * -1).toString();
    } 
    else if (value === "%") {
        display.value = (parseFloat(display.value) / 100).toString();
    } 
    else if (value === "sqrt") {
        display.value = Math.sqrt(parseFloat(display.value)).toString();
    } 
    else {
        if (display.value === "0") {
            display.value = value;
        } else {
            display.value += value;
        }
    }
}

async function calculate() {
    const expr = display.value;

    const res = await fetch("/calculate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ expression: expr })
    });

    const data = await res.json();

    if (data.result !== undefined) {
        display.value = data.result;
    } else {
        display.value = "Error";
    }
}