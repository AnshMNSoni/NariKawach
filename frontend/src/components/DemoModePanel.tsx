import { useState, useEffect } from "react";
import { AlertTriangle, CheckCircle, Eye, Play, Pause, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

type RiskLevel = "low" | "medium" | "high";

interface DemoModePanelProps {
  onRiskChange: (level: RiskLevel) => void;
  currentRisk: RiskLevel;
  isTripActive: boolean;
}

const DemoModePanel = ({ onRiskChange, currentRisk, isTripActive }: DemoModePanelProps) => {
  const [isAutoSimulating, setIsAutoSimulating] = useState(false);
  const [simulationStep, setSimulationStep] = useState(0);

  useEffect(() => {
    if (!isAutoSimulating || !isTripActive) {
      setSimulationStep(0);
      return;
    }

    const steps: RiskLevel[] = ["low", "medium", "high"];
    const interval = setInterval(() => {
      setSimulationStep((prev) => {
        const next = prev + 1;
        if (next >= steps.length) {
          setIsAutoSimulating(false);
          return 0;
        }
        onRiskChange(steps[next]);
        return next;
      });
    }, 3000);

    return () => clearInterval(interval);
  }, [isAutoSimulating, isTripActive, onRiskChange]);

  const handleAutoSimulate = () => {
    if (!isTripActive) return;
    setIsAutoSimulating(true);
    setSimulationStep(0);
    onRiskChange("low");
  };

  const stopSimulation = () => {
    setIsAutoSimulating(false);
    setSimulationStep(0);
  };

  const riskButtons: { level: RiskLevel; icon: React.ReactNode; label: string; color: string }[] = [
    {
      level: "low",
      icon: <CheckCircle className="w-4 h-4" />,
      label: "Low",
      color: "bg-safe hover:bg-safe/90 text-white",
    },
    {
      level: "medium",
      icon: <Eye className="w-4 h-4" />,
      label: "Medium",
      color: "bg-monitoring hover:bg-monitoring/90 text-white",
    },
    {
      level: "high",
      icon: <AlertTriangle className="w-4 h-4" />,
      label: "High",
      color: "bg-emergency hover:bg-emergency/90 text-white",
    },
  ];

  return (
    <div className="fixed bottom-24 left-4 right-4 z-50 mx-auto max-w-lg">
      <div className="bg-card/95 backdrop-blur-lg rounded-2xl shadow-lg border-2 border-primary/30 p-4 animate-slide-up">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="bg-primary/10 text-primary border-primary/30">
              <Zap className="w-3 h-3 mr-1" />
              Demo Mode
            </Badge>
          </div>
          {!isTripActive && (
            <span className="text-xs text-muted-foreground">Start a trip to simulate</span>
          )}
        </div>

        {isTripActive ? (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground flex-shrink-0">Set Risk:</span>
              <div className="flex gap-2 flex-1">
                {riskButtons.map(({ level, icon, label, color }) => (
                  <Button
                    key={level}
                    size="sm"
                    onClick={() => {
                      stopSimulation();
                      onRiskChange(level);
                    }}
                    disabled={isAutoSimulating}
                    className={`flex-1 ${
                      currentRisk === level ? color : "bg-muted text-muted-foreground"
                    }`}
                  >
                    {icon}
                    <span className="ml-1 text-xs">{label}</span>
                  </Button>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-2">
              {isAutoSimulating ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={stopSimulation}
                  className="w-full border-destructive/30 text-destructive"
                >
                  <Pause className="w-4 h-4 mr-2" />
                  Stop Simulation
                </Button>
              ) : (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleAutoSimulate}
                  className="w-full"
                >
                  <Play className="w-4 h-4 mr-2" />
                  Auto Escalate (Low → High)
                </Button>
              )}
            </div>

            {isAutoSimulating && (
              <div className="flex items-center justify-center gap-2 py-2">
                <div className="flex gap-1">
                  {["low", "medium", "high"].map((step, i) => (
                    <div
                      key={step}
                      className={`w-2 h-2 rounded-full transition-all ${
                        i <= simulationStep
                          ? i === 0
                            ? "bg-safe"
                            : i === 1
                            ? "bg-monitoring"
                            : "bg-emergency"
                          : "bg-muted"
                      }`}
                    />
                  ))}
                </div>
                <span className="text-xs text-muted-foreground animate-pulse">
                  Escalating in 3s...
                </span>
              </div>
            )}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground text-center py-2">
            Press "Start Trip" to begin simulation
          </p>
        )}
      </div>
    </div>
  );
};

export default DemoModePanel;
