export default function CampaignSelector({ value, onChange, campaigns = [] }) {
  return (
    <label className="field">
      <span>Campaign</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">All campaigns</option>
        {campaigns.map((campaign) => (
          <option key={campaign.campaign_id} value={campaign.campaign_id}>
            {campaign.campaign_id}
          </option>
        ))}
      </select>
    </label>
  );
}
