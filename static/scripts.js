function to_12hr(time) {
    let hour = Number(time.slice(0, 2));
    let minute = time.slice(3);
    let period = "PM";
    if (hour > 12) {
        hour = hour - 12;
        period = "PM";

    }

    else if (hour[0] === 0) {
        hour = hour[1];

    }

    else if (hour === 12) {
        period = "PM";
    }
    else if (hour === 0) {
        hour = 12;
        period = "AM";

    }

    else {
        period = "AM";
    }


    return `${hour}:${minute} ${period}`

}
document.addEventListener('DOMContentLoaded', function() {
    const rows = document.querySelector('tbody');
    console.log(rows)
    let times = [];
    let days = [];
    for (let i = 0; i <rows.children.length; i++) {
        const row = rows.children[i].innerText.split('\t');
        times.push([to_12hr(row[1]), to_12hr(row[2])]);
        days.push(row[0]);

    }
    console.log(times);
    for (let i = 0; i < times.length; i++) {
        let num = document.getElementById("id").innerText;
        console.log(num);
        let id = num + "appt";
        document.getElementById(id).innerHTML = times[i][0];
        document.getElementById(id).innerHTML = times[i][1];




    }});