import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import type { Score } from "../api/types";
import { buildTierMarkerIcon } from "./map/tierMarkerIcon";
import { MapLegend } from "./map/MapLegend";
import { ScoreCard } from "./ScoreCard";

const LAHORE_CENTER: [number, number] = [31.5497, 74.3436];

interface MapViewProps {
  scores: Score[];
}

export function MapView({ scores }: MapViewProps) {
  return (
    <div className="flex flex-col gap-2">
      <MapLegend />
      <div className="h-[60vh] w-full overflow-hidden rounded-2xl border border-slate-200 shadow-sm md:h-[70vh]">
        <MapContainer center={LAHORE_CENTER} zoom={11} scrollWheelZoom className="h-full w-full">
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {scores.map((score) => (
            <Marker
              key={score.id}
              position={[score.lat, score.lon]}
              icon={buildTierMarkerIcon(score.tier, score.confidence)}
            >
              <Popup minWidth={240}>
                <ScoreCard score={score} compact />
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
}
