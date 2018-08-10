angular.module("loginForm").component("loginForm", {
    templateUrl: "/static/app/login-form/login-form.template.html",
    controller: "loginFormController",
    bindings: {
        successCallback: "=",
        failureCallback: "="
    }
});