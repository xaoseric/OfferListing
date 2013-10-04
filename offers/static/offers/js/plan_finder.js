var ordering = $("#orderingSelect");

var multi_fields = [
    {
        selector: $("#countrySelect"),
        api: "location__country"
    },
    {
        selector: $("#providerSelect"),
        api: "offer__provider__id"
    },
    {
        selector: $("#billingSelect"),
        api: "billing_time"
    },
    {
        selector: $("#datacenterSelect"),
        api: "location__datacenter__id"
    },
    {
        selector: $("#serverTypeSelect"),
        api: "server_type"
    }
];

var min_max_fields = [
    {
        minField: $("#planMemMin"),
        maxField: $("#planMemMax"),
        api: 'memory'
    },
    {
        minField: $("#planHDDMin"),
        maxField: $("#planHDDMax"),
        api: "disk_space"
    },
    {
        minField: $("#planBandMin"),
        maxField: $("#planBandMax"),
        api: 'bandwidth'
    },
    {
        minField: $("#planIPv4Min"),
        maxField: $("#planIPv4Max"),
        api: 'ipv4_space'
    },
    {
        minField: $("#planIPv6Min"),
        maxField: $("#planIPv6Max"),
        api: 'ipv6_space'
    },
    {
        minField: $("#planCostMin"),
        maxField: $("#planCostMax"),
        api: 'cost'
    }
];


function makePagination(meta_data){

    var previous_disabled = '';
    var previous_data = '';
    var next_disabled = '';
    var next_data = '';

    var total_pages = Math.ceil(meta_data.total_count/meta_data.limit);
    var current_page = Math.ceil(meta_data.offset / meta_data.limit) + 1;

    if (meta_data.previous == null){
      previous_disabled = 'disabled';
    } else {
      previous_data = meta_data.previous;
    }

    if (meta_data.next == null){
      next_disabled = 'disabled';
    } else {
      next_data = meta_data.next;
    }


    return '<ul class="pagination">\
            <li class="' + previous_disabled + '">\
              <a onclick="paginationNavigate(\'' + previous_data +'\')">&laquo;</a>\
            </li>\
            <li><a>Page ' + current_page + ' of ' + total_pages + '</a></li>\
            <li class="' + next_disabled + '">\
              <a onclick="paginationNavigate(\'' + next_data + '\')">&raquo;</a>\
            </li>\
        </ul>'
}

function paginationNavigate(url){
    if(url.length > 0){
      getAndRender(url);
    }
}

function getAndRender(url){
    var endpoint_data = $("#plan_list");
    endpoint_data.html('<div class="ajax-loading"></div>');

    $.get(
       url,
       function(data) {
         endpoint_data.html("");

         if (data.meta.total_count == 0){
           endpoint_data.html("No plans with your filtering found!");
           return;
         }

         for (var counter=0; counter < data["objects"].length; counter++){
           var plan = data["objects"][counter];
           endpoint_data.append(plan.html);
         }
         endpoint_data.append(makePagination(data["meta"]));
       }
    ).fail(function(){
        endpoint_data.html("There were errors in your filtering. Please check that you did not enter letters or " +
            "punctuation in the numerically filtered fields.")
    });
}

function filterPlans(){
    var urlOptions = {
        "limit": 3,
        "format": "json"
    };

    // Go through all the multi choice fields
    for (var select_counter = 0; select_counter < multi_fields.length; select_counter++){
        var select_field = multi_fields[select_counter];
        if (select_field.selector.val() != null){
            urlOptions[select_field.api + "__in"] = select_field.selector.val().join(',');
        }
    }

    // Go through all the min max fields
    for (var min_max_counter = 0; min_max_counter < min_max_fields.length; min_max_counter++){
        var min_max = min_max_fields[min_max_counter];
        if(min_max.minField.val().length > 0){
            urlOptions[min_max.api + '__gte'] = min_max.minField.val();
        }
        if(min_max.maxField.val().length > 0){
            urlOptions[min_max.api + '__lte'] = min_max.maxField.val();
        }
    }

    // Ordering
    if (ordering.val() != "ALL"){
        urlOptions["order_by"] = ordering.val();
    }

    var urlParameters = $.param(urlOptions);

    getAndRender('/find/data/main/plan/?' + urlParameters);

}

$(document).ready(filterPlans);
