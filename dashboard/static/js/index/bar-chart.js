document.addEventListener("DOMContentLoaded", function() {
    // Bar chart
    
    // console.log(getTableData())
    function buildChart(tableData){
        var myChart = new Chart(document.getElementById("chartjs-bar"), {
            type: "bar",
            data: {
                labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                datasets: [{
                    label: "Complete",
                    backgroundColor: window.theme.success,
                    borderColor: window.theme.success,
                    hoverBackgroundColor: window.theme.success,
                    hoverBorderColor: window.theme.success,
                    data: tableData.success,
                    barPercentage: .75,
                    categoryPercentage: .5
                }, {
                    label: "In Progress",
                    backgroundColor: window.theme.warning,
                    borderColor: window.theme.warning,
                    hoverBackgroundColor: window.theme.warning,
                    hoverBorderColor: window.theme.warning,
                    data: tableData.in_progress,
                    barPercentage: .75,
                    categoryPercentage: .5
                }, {
                    label: "Failed",
                    backgroundColor: window.theme.danger,
                    borderColor: window.theme.danger,
                    hoverBackgroundColor: window.theme.danger,
                    hoverBorderColor: window.theme.danger,
                    data: tableData.failure,
                    barPercentage: .75,
                    categoryPercentage: .5
                }]
            },
            options: {
                maintainAspectRatio: false,
                legend: {
                    display: false
                },
                scales: {
                    yAxes: [{
                        gridLines: {
                            display: false
                        },
                        stacked: false,
                        ticks: {
                            stepSize: 20
                        }
                    }],
                    xAxes: [{
                        stacked: false,
                        gridLines: {
                            color: "transparent"
                        }
                    }]
                }
            }
        });
    }

    
    var tableData;      
    var url = "/data";

    var xhr = new XMLHttpRequest();
    

    xhr.onreadystatechange = function () {
    if (xhr.readyState == 4) {
        tableData = JSON.parse(xhr.response);
        console.log(tableData)
        buildChart(tableData)
    }};
    xhr.open("GET", url);
    xhr.send();
    
    
});