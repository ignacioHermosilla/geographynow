// Based On https://github.com/chrisdavidmills/push-api-demo/blob/283df97baf49a9e67705ed08354238b83ba7e9d3/main.js

var isPushEnabled = false,
  subBtn,
  registration;

function serviceWorkerRegister(){
      // Do everything if the Browser Supports Service Worker
      if ('serviceWorker' in navigator) { 
        var serviceWorker = document.getElementById('service-worker-js').src;
        navigator.serviceWorker.register(serviceWorker)
          .then(
            function(reg) {
              registration = reg;
              initialiseSubscription(reg);
            }
          );
      }
}

  // Once the service worker is registered set the initial state  
  function initialiseSubscription(reg) {
    // Are Notifications supported in the service worker?  
    if (!(reg.showNotification)) {
        // Show a message and activate the button
        return;
    }

    // Check the current Notification permission.  
    // If its denied, it's a permanent block until the  
    // user changes the permission  
    if (Notification.permission === 'denied') {
      // Show a message and activate the button
      return;  
    }

    // Check if push messaging is supported  
    if (!('PushManager' in window)) {
      // Show a message and activate the button 
      return;  
    }

    // We need to subscribe for push notification and send the information to server 
    subscribe(reg)
}

function subscribe(reg) {
  // Get the Subscription or register one
  getSubscription(reg)
    .then(
      function(subscription) {
        postSubscribeObj('subscribe',subscription);
      }
    )
    .catch(
      function(error) {
        console.log('Subscription error.', error)
      }
    )
}

function getSubscription(reg) {
    return reg.pushManager.getSubscription()
      .then(
        function(subscription) {
          // Check if Subscription is available
          if (subscription) {
            return subscription;
          }
          // If not, register one
          return registration.pushManager.subscribe({ userVisibleOnly: true });
        }
      )
}

function unsubscribe() {
  // Get the Subscription to unregister
  registration.pushManager.getSubscription()
    .then(
      function(subscription) {

        // Check we have a subscription to unsubscribe
        if (!subscription) {
          // No subscription object, so set the state
          // to allow the user to subscribe to push
          return;
        }
        postSubscribeObj('unsubscribe', subscription);
      }
    )  
}

function postSubscribeObj(statusType, subscription) {
  // Send the information to the server with fetch API.
  // the type of the request, the name of the user subscribing, 
  // and the push subscription endpoint + key the server needs
  // to send push messages
  
  var browser = navigator.userAgent.match(/(firefox|msie|chrome|safari|trident)/ig)[0].toLowerCase(),
    data = {  status_type: statusType,
              subscription: subscription.toJSON(),
              browser: browser,
           };

  fetch('/subscribe_or_unsubscribe_notification', {
    method: 'post',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data),
    credentials: 'include'
  })
    .then(
      function(response) {
        // Check the information is saved successfully into server
        if ((response.status == 201) && (statusType == 'subscribe')) {
          // Show unsubscribe button instead
          isPushEnabled = true;
        }

        // Check if the information is deleted from server
        if ((response.status == 202) && (statusType == 'unsubscribe')) {
          // Get the Subscription
          getSubscription(registration)
            .then(
              function(subscription) {
                // Remove the subscription
                subscription.unsubscribe()
                .then(
                  function(successful) {
                    isPushEnabled = false;
                  }
                )
              }
            )
            .catch(
              function(error) {
              }
            );
        }
      }
    )
}