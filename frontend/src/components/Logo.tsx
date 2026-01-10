import { Shield } from "lucide-react";

interface LogoProps {
  size?: "sm" | "md" | "lg";
  showTagline?: boolean;
}

const Logo = ({ size = "md", showTagline = false }: LogoProps) => {
  const sizeConfig = {
    sm: {
      container: "w-9 h-9",
      icon: "w-4 h-4",
      text: "text-base",
      tagline: "text-[10px]",
    },
    md: {
      container: "w-11 h-11",
      icon: "w-5 h-5",
      text: "text-lg",
      tagline: "text-xs",
    },
    lg: {
      container: "w-16 h-16",
      icon: "w-8 h-8",
      text: "text-2xl",
      tagline: "text-sm",
    },
  };

  const config = sizeConfig[size];

  return (
    <div className="flex items-center gap-3">
      <div className={`${config.container} rounded-2xl bg-gradient-to-br from-primary via-primary to-primary/70 flex items-center justify-center shadow-calm relative overflow-hidden`}>
        {/* Inner glow effect */}
        <div className="absolute inset-0 bg-gradient-to-tr from-white/20 to-transparent" />
        <Shield className={`${config.icon} text-primary-foreground relative z-10`} />
      </div>
      <div className="flex flex-col">
        <span className={`${config.text} font-display font-bold text-foreground tracking-tight`}>
          Nari<span className="text-primary">Kawach</span>
        </span>
        {showTagline && (
          <span className={`${config.tagline} text-muted-foreground`}>
            Your Safety Companion
          </span>
        )}
      </div>
    </div>
  );
};

export default Logo;
