var app = angular.module("fmshoes", ["ngRoute", "ngResource", "fmshoes.services"]);

var services = angular.module("fmshoes.services", ["ngResource"]);

services.factory('Search', function($resource) {
    return $resource("http://127.0.0.1:5000/api/v1/search", {q: '@q'}, {
        query: { method: 'GET', isArray: true}
    });
});

app.config(function($routeProvider) {
    $routeProvider.when('/', {
        templateUrl: 'search.html',
        controller: 'mainController'
    });
});

app.controller('mainController',
    function($scope, Search) {
        $scope.search = function() {
            q = $scope.searchString;
            if(q.length > 1) {
                $scope.results = Search.query({q: q});
                $scope.have_query = true;
            } else 
                $scope.have_query = false;
        }
    }
);
