angular.module("recordList").component("recordList", {
    templateUrl: "/static/app/record-list/record-list.template.html",
    controller: "recordListController",
    bindings: {
        items: "=",
        definition: "="
    }
});