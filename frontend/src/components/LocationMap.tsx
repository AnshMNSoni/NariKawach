import { useEffect, useState, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { MapPin, Navigation, AlertCircle } from "lucide-react";

// Fix Leaflet default marker icon issue (Vite + React)
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
});

interface LocationMapProps {
  isTracking: boolean;
  onLocationUpdate?: (lat: number, lng: number) => void;
}

interface LocationState {
  lat: number;
  lng: number;
  accuracy: number;
}

const LocationMap = ({ isTracking, onLocationUpdate }: LocationMapProps) => {
  const [location, setLocation] = useState<LocationState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [permissionDenied, setPermissionDenied] = useState(false);

  const mapRef = useRef<L.Map | null>(null);
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const markerRef = useRef<L.Marker | null>(null);
  const circleRef = useRef<L.Circle | null>(null);
  const watchIdRef = useRef<number | null>(null);

  /* -------------------------------
     Initialize Map (ONLY when tracking)
  -------------------------------- */
  useEffect(() => {
    if (!isTracking) return;
    if (!mapContainerRef.current) return;
    if (mapRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [20.5937, 78.9629], // India fallback
      zoom: 16,
      zoomControl: false,
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);

    mapRef.current = map;

    // 🔑 Fix size issue when container appears
    setTimeout(() => {
      map.invalidateSize();
    }, 0);

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, [isTracking]);

  /* -------------------------------
     Update marker when location changes
  -------------------------------- */
  useEffect(() => {
    if (!mapRef.current || !location) return;

    const { lat, lng, accuracy } = location;

    if (!markerRef.current) {
      const customIcon = L.divIcon({
        className: "custom-marker",
        html: `<div style="
          width: 22px;
          height: 22px;
          background: hsl(var(--primary));
          border-radius: 50%;
          border: 3px solid white;
          box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        "></div>`,
        iconSize: [22, 22],
        iconAnchor: [11, 11],
      });

      markerRef.current = L.marker([lat, lng], {
        icon: customIcon,
      }).addTo(mapRef.current);
    } else {
      markerRef.current.setLatLng([lat, lng]);
    }

    if (!circleRef.current) {
      circleRef.current = L.circle([lat, lng], {
        radius: accuracy,
        color: "hsl(var(--primary))",
        fillColor: "hsl(var(--primary))",
        fillOpacity: 0.1,
        weight: 2,
      }).addTo(mapRef.current);
    } else {
      circleRef.current.setLatLng([lat, lng]);
      circleRef.current.setRadius(accuracy);
    }

    mapRef.current.setView([lat, lng], mapRef.current.getZoom());
  }, [location]);

  /* -------------------------------
     Geolocation Tracking
  -------------------------------- */
  useEffect(() => {
    if (!isTracking) {
      if (watchIdRef.current !== null) {
        navigator.geolocation.clearWatch(watchIdRef.current);
        watchIdRef.current = null;
      }
      return;
    }

    if (!navigator.geolocation) {
      setError("Geolocation not supported");
      return;
    }

    watchIdRef.current = navigator.geolocation.watchPosition(
      (pos) => {
        const newLocation = {
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
          accuracy: pos.coords.accuracy,
        };
        setLocation(newLocation);
        setError(null);
        onLocationUpdate?.(newLocation.lat, newLocation.lng);
      },
      (err) => {
        if (err.code === err.PERMISSION_DENIED) {
          setPermissionDenied(true);
          setError("Permission denied");
        } else {
          setError("Unable to fetch location");
        }
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 5000,
      }
    );

    return () => {
      if (watchIdRef.current !== null) {
        navigator.geolocation.clearWatch(watchIdRef.current);
      }
    };
  }, [isTracking, onLocationUpdate]);

  /* -------------------------------
     UI States
  -------------------------------- */

  if (!isTracking) {
    return (
      <div className="aspect-video bg-muted/40 rounded-2xl border flex items-center justify-center">
        <div className="text-center">
          <MapPin className="w-8 h-8 text-primary mx-auto mb-2" />
          <p className="text-sm text-muted-foreground">
            Start a trip to enable live tracking
          </p>
        </div>
      </div>
    );
  }

  if (permissionDenied) {
    return (
      <div className="aspect-video bg-destructive/10 rounded-2xl border flex items-center justify-center">
        <div className="text-center px-4">
          <AlertCircle className="w-8 h-8 text-destructive mx-auto mb-2" />
          <p className="text-sm font-medium">
            Location permission required
          </p>
          <p className="text-xs text-muted-foreground">
            Enable location access in browser settings
          </p>
        </div>
      </div>
    );
  }

  if (error && !location) {
    return (
      <div className="aspect-video bg-muted/40 rounded-2xl border flex items-center justify-center">
        <div className="text-center">
          <Navigation className="w-8 h-8 text-primary mx-auto mb-2 animate-pulse" />
          <p className="text-sm text-muted-foreground">
            Acquiring location…
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="aspect-video rounded-2xl overflow-hidden border shadow-soft">
      <div
        ref={mapContainerRef}
        style={{ height: "100%", width: "100%" }}
      />
    </div>
  );
};

export default LocationMap;
