document.addEventListener('DOMContentLoaded', function () {
    const rainfallSlider = document.getElementById('rainfall');
    const rainfallValue = document.getElementById('rainfall-value');

    rainfallSlider.addEventListener('input', () => {
        rainfallValue.textContent = rainfallSlider.value;
    });
    const iframe = document.querySelector('iframe');
    if (iframe) {
        iframe.onload = function () {
            // Access the iframe's document (try both methods for compatibility)
            const iframeDocument = iframe.contentDocument || iframe.contentWindow.document;
            iframeDocument.addEventListener('DOMContentLoaded', function () {
                const mapContainer = iframeDocument.querySelector('.folium-map');
                if (mapContainer) {
                    const mapId = mapContainer.id;
                    const map = L.map(mapId);
                    console.log(map)

                    // Add shapefile
                    // var shpfile = new L.Shapefile('your_shapefile.zip');
                    // shpfile.addTo(map);

                    map.on('click', function (e) {
                        console.log('click detected')
                        const clickedCoords = [e.latlng.lat, e.latlng.lng];
                        const closestNodeID = findClosestNode(clickedCoords);

                        // 1. Display a popup with node information (example)
                        const nodeInfo = nodes.find(node => node.nodeID === closestNodeID);
                        if (nodeInfo) {
                            const popupContent = `
                        Node ID: ${nodeInfo.nodeID}<br>
                        Coordinates: ${nodeInfo.xCoord}, ${nodeInfo.yCoord}
                    `;
                            L.popup()
                                .setLatLng(e.latlng)
                                .setContent(popupContent)
                                .openOn(map);
                        }

                        // 2. Populate the origin/destination input fields
                        // Check if origin is already set, if not set origin, otherwise set destination
                        if (document.getElementById("origin").value === "") {
                            document.getElementById("origin").value = closestNodeID;
                        } else {
                            document.getElementById("destination").value = closestNodeID;
                        }

                        // 3. Add a marker to the map
                        L.marker(e.latlng, { draggable: false }).addTo(map);
                    });
                } else {
                    console.error(".folium-map container not found within the iframe!");
                }
            }
            )
        }
    } else {
        console.error("Iframe not found!");
    }

});


function setOrigin(nodeID) {
    document.getElementById("origin_display").textContent = nodeID;
    document.getElementById("origin_input").value = nodeID;
}

function setDestination(nodeID) {
    document.getElementById("destination_display").textContent = nodeID;
    document.getElementById("destination_input").value = nodeID;
}

function closeModal() {
    document.getElementById("errorModal").style.display = "none";
}

function findClosestNode(coords) {
    let minDistance = Infinity;
    let closestNode = null;

    // Iterate through your node data (you'll need to pass this from Flask)
    for (const node of nodes) {
        const nodeCoords = [node.xCoord, node.yCoord];
        const distance = calculateDistance(coords, nodeCoords);
        if (distance < minDistance) {
            minDistance = distance;
            closestNode = node.nodeID;
        }
    }
    return closestNode;
}
function calculateDistance(coords1, coords2) {
    const [lat1, lon1] = coords1;
    const [lat2, lon2] = coords2;
    const R = 6371; // Radius of the earth in km
    const dLat = deg2rad(lat2 - lat1);  // deg2rad below
    const dLon = deg2rad(lon2 - lon1);
    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2)
        ;
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const d = R * c; // Distance in km
    return d;
}

function deg2rad(deg) {
    return deg * (Math.PI / 180)
}

