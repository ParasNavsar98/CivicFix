import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { Problem } from '../../types';
import { MapComponent } from '../../components/common/MapComponent';
import { useNavigate } from 'react-router-dom';

export const CitizenMapPage: React.FC = () => {
  const [problems, setProblems] = useState<Problem[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    api.getProblems().then(setProblems);
  }, []);

  return (
    <div className="space-y-6 animate-in fade-in">
      <div>
        <h1 className="text-2xl font-extrabold text-[#17332F]">Community Problem GIS Map</h1>
        <p className="text-xs text-[#66736F] mt-1">Explore reported problems across Jharkhand districts while protecting private citizen identities.</p>
      </div>

      <MapComponent
        problems={problems}
        height="h-[600px]"
        onSelectProblem={(prob) => navigate(`/citizen/problems/${prob.problemId}`)}
      />
    </div>
  );
};
