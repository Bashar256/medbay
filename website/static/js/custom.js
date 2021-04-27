$(function () {
    $('#datetimepicker1').datetimepicker({
        inline: true,
    });
});

function pieChart()
{

    var data = {
        labels: ['35%', '55%', '10%'], 
        series: [30, 25, 15]
        };
        
    var options = {
        labelInterpolationFnc: function(value) {
            return value[0]
        }
        };
        
    var responsiveOptions = [
        ['screen and (min-width: 230px)', {
            chartPadding: 10,
            donut: true,
            labelOffset: 40,
            donutWidth: 50,
            labelDirection: 'explode',
            labelInterpolationFnc: function(value) {
            return value;
            }
        }],
        ['screen and (min-width: 230px)', {
            labelOffset: 60,
            chartPadding: 20
        }]
    ];
        
    new Chartist.Pie('#pie-chart', data, options, responsiveOptions);
    
}

function chartBar()
{
        var options = {
        series: [{
        name: 'Likes',
        data: [4, 3, 10, 9, 50, 19, 22, 9, 12, 7, 19, 5, 13, 9, 17, 2, 7, 15]
    }],
        chart: {
        toolbar: {
            show: false,
        },
        height: 120,
        type: 'line',
    },
    stroke: {
        width: 4,
        curve: 'smooth',
        colors: ['#23a287']
    },
    
    legend: {
        show: false
    },
    tooltip: {
        enabled: true,
    },
    
    grid: {
show: false,
},

    xaxis: {
        show: false,
        lines: {
            show: false,
        },
        labels: {
            show: false,
        },
        axisBorder: {
            show: false,
        },
        
    },
    yaxis: {
        show: false,
    },
};

var chart = new ApexCharts(document.querySelector("#chart"), options);
chart.render();
    
}

jQuery(window).on('load',function(){
    setTimeout(function(){
        pieChart();
        chartBar();
        
    }, 1000); 
});