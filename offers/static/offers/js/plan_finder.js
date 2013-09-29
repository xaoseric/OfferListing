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
    $("#plan_list").html('<div class="loading"></div>');

    $.get(
       url,
       function(data) {
         var endpoint_data = $("#plan_list");
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
    );
}

function filterPlans(){
    var urlOptions = {
        "limit": 3,
        "format": "json"
    };

    var country = $("#countrySelect");
    var provider = $("#providerSelect");
    var billing = $("#billingSelect");

    var memMin = $("#planMemMin");
    var memMax = $("#planMemMax");

    var hddMin = $("#planHDDMin");
    var hddMax = $("#planHDDMax");

    var bandMin = $("#planBandMin");
    var bandMax = $("#planBandMax");

    var ipv4Min = $("#planIPv4Min");
    var ipv4Max = $("#planIPv4Max");

    var ipv6Min = $("#planIPv6Min");
    var ipv6Max = $("#planIPv6Max");

    var costMin = $("#planCostMin");
    var costMax = $("#planCostMax");

    var ordering = $("#orderingSelect");

    // Country
    if (country.val() != "ALL"){
        urlOptions["location__country"] = country.val();
    }

    // Provider
    if (provider.val() != "ALL"){
        urlOptions["offer__provider__id"] = provider.val();
    }

    // Billing
    if (billing.val() != "ALL"){
        urlOptions["billing_time"] = billing.val();
    }

    // Memory
    if(memMin.val().length > 0){
        urlOptions["memory__gte"] = memMin.val();
    }

    if(memMax.val().length > 0){
        urlOptions["memory__lte"] = memMax.val();
    }

    // Disk space
    if(hddMin.val().length > 0){
        urlOptions["disk_space__gte"] = hddMin.val();
    }

    if(hddMax.val().length > 0){
        urlOptions["disk_space__lte"] = hddMax.val();
    }

    // Bandwidth
    if(bandMin.val().length > 0){
        urlOptions["bandwidth__gte"] = bandMin.val();
    }

    if(bandMax.val().length > 0){
        urlOptions["bandwidth__lte"] = bandMax.val();
    }

    // IPv4 Space
    if(ipv4Min.val().length > 0){
        urlOptions["ipv4_space__gte"] = ipv4Min.val();
    }

    if(ipv4Max.val().length > 0){
        urlOptions["ipv4_space__lte"] = ipv4Max.val();
    }

    // IPv6 Space
    if(ipv6Min.val().length > 0){
        urlOptions["ipv6_space__gte"] = ipv6Min.val();
    }

    if(ipv6Max.val().length > 0){
        urlOptions["ipv6_space__lte"] = ipv6Max.val();
    }

    // Cost
    if(costMin.val().length > 0){
        urlOptions["cost__gte"] = costMin.val();
    }

    if(costMax.val().length > 0){
        urlOptions["cost__lte"] = costMax.val();
    }

    // Ordering
    if (ordering.val() != "ALL"){
        urlOptions["order_by"] = ordering.val();
    }

    var urlParameters = $.param(urlOptions);

    getAndRender('/find/data/main/plan/?' + urlParameters);

}

$(document).ready(filterPlans);