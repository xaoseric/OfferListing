class PlanFinder
  ordering = $("#orderingSelect")

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
      min_max.minField.on 'input', filterPlans
      min_max.maxField.on 'input', filterPlans

  makePagination = (meta_data, endpoint) ->

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



      endpoint.append """
          <ul class='pagination'>
            <li class='#{previous_disabled}'>
              <a id='plan-finder-prev'>&laquo;</a>
            </li>
            <li><a>Page #{current_page} of #{total_pages}</a></li>
            <li class='#{next_disabled}'>
              <a id='plan-finder-next'>&raquo;</a>
            </li>
          </ul>
      """

      $("#plan-finder-prev").click(() -> paginationNavigate(previous_data))
      $("#plan-finder-next").click(() -> paginationNavigate(next_data))

      return

  paginationNavigate = (url) ->
      if url.length > 0
        getAndRender(url)

  getAndRender = (url) ->
      endpoint_data = $("#plan_list")
      endpoint_data.html '<div class="ajax-loading"></div>'

      currentRequest = $.get(
         url,
         (data) ->
           endpoint_data.html ""

           if data.meta.total_count == 0
             endpoint_data.html "No plans with your filtering found!"
             return

           for plan in data["objects"]
             endpoint_data.append plan.html

           makePagination data["meta"], endpoint_data

           return
      ).fail(() ->
        endpoint_data.html """
            There were errors in your filtering. Please check that you did not enter letters or punctuation in the
            numerically filtered fields.
        """
        return
      )

      return

  filterPlans = () ->
    urlOptions =
        limit: 3
        format: "json"

    try
        currentRequest.abort()
    catch error

    for select_field in multi_fields
      if select_field.selector.val() != null
        urlOptions[select_field.api + "__in"] = select_field.selector.val().join ','

    for min_max in min_max_fields
      if min_max.minField.val().length > 0
        urlOptions[min_max.api + '__gte'] = min_max.minField.val()
      if min_max.maxField.val().length > 0
        urlOptions[min_max.api + '__lte'] = min_max.maxField.val()

    # Ordering
    if ordering.val() != "ALL"
      urlOptions["order_by"] = ordering.val()


    urlParameters = $.param(urlOptions);

    getAndRender '/find/data/main/plan/?' + urlParameters

    return

  $(document).ready(() ->
    setupInputTriggers()
    filterPlans()
    return
  )
  $("#filter-plans-btn").on 'click', filterPlans
