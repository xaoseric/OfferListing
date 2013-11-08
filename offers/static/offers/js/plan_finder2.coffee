ordering = $("order fields")

multi_fields = [
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
]

min_max_fields = [
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
        minField: $("#planCoreMin"),
        maxField: $("#planCoreMax"),
        api: 'cpu_cores'
    },
    {
        minField: $("#planCostMin"),
        maxField: $("#planCostMax"),
        api: 'cost'
    }
]

### Main logic ###
currentRequest = null

setupInputTriggers = () ->
  for select_field in multi_fields
    select_field.selector.change filterPlans

  for min_max in min_max_fields
    min_max.minField.on('input', filterPlans)
    min_max.maxField.on('input', filterPlans)

do setupInputTriggers

makePagination = (meta_data) ->

    previous_disabled = '';
    previous_data = '';
    next_disabled = '';
    next_data = '';

    total_pages = Math.ceil(meta_data.total_count/meta_data.limit);
    current_page = Math.ceil(meta_data.offset / meta_data.limit) + 1;

    if meta_data.previous == null
      previous_disabled = 'disabled'
    else
      previous_data = meta_data.previous


    if meta_data.next == null
      next_disabled = 'disabled'
    else
      next_data = meta_data.next



    return """
        <ul class='pagination'>
          <li class='#{previous_disabled}'>
            <a onclick='paginationNavigate("#{previous_data}")'>&laquo;</a>
          </li>
          <li><a>Page #{current_page} of #{total_pages}</a></li>
          <li class='#{next_disabled}'>
            <a onclick='paginationNavigate("#{next_data}")'>&raquo;</a>
          </li>
        </ul>
    """
