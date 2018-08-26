angular.module("drilldownList").component("drilldownList", {
    templateUrl: "/static/app/drilldown-list/drilldown-list.template.html",
    controller: "drilldownController",
    bindings: {
        selectCallback: "=",
        items: "="
    }
});