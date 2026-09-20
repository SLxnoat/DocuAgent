import { useState } from "react";
import { Cpu } from "lucide-react";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";

interface OptionsPanelProps {
  outputFormats: ("markdown" | "html" | "pdf")[];
  onChangeFormats: (formats: ("markdown" | "html" | "pdf")[]) => void;
  language: string;
  onChangeLanguage: (lang: string) => void;
  domainHint: string;
  onChangeDomainHint: (domain: string) => void;
  selectedModel: string;
  onChangeModel: (model: string) => void;
  availableModels?: string[];
}

const DEFAULT_MODEL_PRESETS = [
  "llama3.3:70b",
  "llama3.1:8b",
  "qwen2.5:72b",
  "qwen2.5:32b",
  "qwen2.5:7b",
  "mistral-large",
  "deepseek-r1:70b",
];

export function OptionsPanel({
  outputFormats,
  onChangeFormats,
  language,
  onChangeLanguage,
  domainHint,
  onChangeDomainHint,
  selectedModel,
  onChangeModel,
  availableModels = DEFAULT_MODEL_PRESETS,
}: OptionsPanelProps) {
  const [isCustomModel, setIsCustomModel] = useState(
    () => !availableModels.includes(selectedModel),
  );

  const toggleFormat = (format: "markdown" | "html" | "pdf") => {
    if (outputFormats.includes(format)) {
      if (outputFormats.length > 1) {
        onChangeFormats(outputFormats.filter((f) => f !== format));
      }
    } else {
      onChangeFormats([...outputFormats, format]);
    }
  };

  const handleModelSelect = (val: string) => {
    if (val === "custom") {
      setIsCustomModel(true);
    } else {
      setIsCustomModel(false);
      onChangeModel(val);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 p-4 rounded-lg bg-muted/40 border">
      {/* 1. AI Model Selection */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <Label
            htmlFor="model-select"
            className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5"
          >
            <Cpu className="h-3.5 w-3.5 text-brand" />
            AI Model
          </Label>
          <span className="text-[10px] text-muted-foreground font-mono">
            Ollama
          </span>
        </div>

        {!isCustomModel ? (
          <div className="space-y-1.5">
            <Select
              value={
                availableModels.includes(selectedModel)
                  ? selectedModel
                  : "custom"
              }
              onValueChange={handleModelSelect}
            >
              <SelectTrigger
                id="model-select"
                className="h-9 font-mono text-xs"
              >
                <SelectValue placeholder="Select LLM Model" />
              </SelectTrigger>
              <SelectContent>
                {availableModels.map((m) => (
                  <SelectItem key={m} value={m} className="font-mono text-xs">
                    {m} {m.includes("70b") || m.includes("72b") ? "✨" : ""}
                  </SelectItem>
                ))}
                <SelectItem
                  value="custom"
                  className="text-xs text-brand font-medium"
                >
                  + Custom / Other Model...
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        ) : (
          <div className="flex gap-1.5 items-center">
            <Input
              id="model-custom"
              placeholder="e.g. llama3.3:70b"
              value={selectedModel}
              onChange={(e) => onChangeModel(e.target.value)}
              className="h-9 font-mono text-xs"
              autoFocus
            />
            <button
              type="button"
              onClick={() => {
                setIsCustomModel(false);
                onChangeModel(availableModels[0] || "llama3.3:70b");
              }}
              className="text-[10px] text-muted-foreground hover:text-foreground underline px-1 shrink-0"
              title="Return to preset list"
            >
              presets
            </button>
          </div>
        )}
      </div>

      {/* 2. Output Formats */}
      <div className="flex flex-col gap-2">
        <Label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          Export Formats
        </Label>
        <div className="flex items-center gap-3 pt-1.5">
          <div className="flex items-center space-x-1.5">
            <Checkbox
              id="fmt-md"
              checked={outputFormats.includes("markdown")}
              onCheckedChange={() => toggleFormat("markdown")}
            />
            <label
              htmlFor="fmt-md"
              className="text-xs font-medium leading-none cursor-pointer"
            >
              Markdown
            </label>
          </div>
          <div className="flex items-center space-x-1.5">
            <Checkbox
              id="fmt-html"
              checked={outputFormats.includes("html")}
              onCheckedChange={() => toggleFormat("html")}
            />
            <label
              htmlFor="fmt-html"
              className="text-xs font-medium leading-none cursor-pointer"
            >
              HTML
            </label>
          </div>
          <div className="flex items-center space-x-1.5">
            <Checkbox
              id="fmt-pdf"
              checked={outputFormats.includes("pdf")}
              onCheckedChange={() => toggleFormat("pdf")}
            />
            <label
              htmlFor="fmt-pdf"
              className="text-xs font-medium leading-none cursor-pointer"
            >
              PDF
            </label>
          </div>
        </div>
      </div>

      {/* 3. Target Language */}
      <div className="flex flex-col gap-2">
        <Label
          htmlFor="lang-select"
          className="text-xs font-semibold text-muted-foreground uppercase tracking-wider"
        >
          Document Language
        </Label>
        <Select value={language} onValueChange={onChangeLanguage}>
          <SelectTrigger id="lang-select" className="h-9 text-xs">
            <SelectValue placeholder="Select Language" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="en">English (US)</SelectItem>
            <SelectItem value="es">Spanish</SelectItem>
            <SelectItem value="fr">French</SelectItem>
            <SelectItem value="de">German</SelectItem>
            <SelectItem value="ja">Japanese</SelectItem>
            <SelectItem value="zh">Chinese</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* 4. Domain Context Override */}
      <div className="flex flex-col gap-2">
        <Label
          htmlFor="domain-hint"
          className="text-xs font-semibold text-muted-foreground uppercase tracking-wider"
        >
          Domain Hint (Optional)
        </Label>
        <Input
          id="domain-hint"
          placeholder="e.g. SaaS Admin, Banking"
          value={domainHint}
          onChange={(e) => onChangeDomainHint(e.target.value)}
          className="h-9 text-xs"
        />
      </div>
    </div>
  );
}
