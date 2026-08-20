import { useState } from "react";
import { CompanyPage } from "./pages/CompanyPage";
import { PortfolioDashboard } from "./pages/PortfolioDashboard";

export function App() {
  const [selectedCompanyId, setSelectedCompanyId] = useState<number | null>(null);
  return selectedCompanyId ? <CompanyPage companyId={selectedCompanyId} onBack={() => setSelectedCompanyId(null)} /> : <PortfolioDashboard onSelectCompany={setSelectedCompanyId} />;
}
