# Compliance Draft — SUN-5K-G06P3-EU-AM2-P1

Prepared for SunBridge's import agent. This draft summarizes what the two supplier datasheets say about this inverter, where they agree, and what still needs to be confirmed before the paperwork is finalized.

**Source documents:**
- data\input\datasheet_sun-4-12k-g06p3-eu-am2-p1_231007_en.pdf
- data\input\datasheet_sun-4-15k-g06p3-eu-am2_240318_en.pdf

**Overall status:** conflict

## ⚠ What Needs Attention Before Filing

- **model** (critical): The two source documents identify the product with different model codes: source 1 uses 'SUN-5K-G06P3-EU-AM2-P1' and source 2 uses 'SUN-5K-G06P3-EU-AM2'. This may mean the two documents describe different variants of the same base product rather than an identical part.
  - *Recommendation:* Confirm with the manufacturer/SunBridge whether these codes represent the same shippable unit or genuinely different variants before relying on either datasheet as authoritative for compliance.
- **rated_output_voltage_range_v** (high): The value for 'rated_output_voltage_range_v' differs between the two source documents.
  - *Recommendation:* Review both source documents and determine whether the difference represents a product revision, specification change, or extraction issue.
- **cooling_concept** (high): The value for 'cooling_concept' differs between the two source documents.
  - *Recommendation:* Review both source documents and determine whether the difference represents a product revision, specification change, or extraction issue.
- **ingress_protection** (high): The value for 'ingress_protection' differs between the two source documents.
  - *Recommendation:* Review both source documents and determine whether the difference represents a product revision, specification change, or extraction issue.
- **permissible_altitude_m** (high): The value for 'permissible_altitude_m' differs between the two source documents.
  - *Recommendation:* Review both source documents and determine whether the difference represents a product revision, specification change, or extraction issue.
- **weight_kg** (high): The value for 'weight_kg' differs between the two source documents.
  - *Recommendation:* Review both source documents and determine whether the difference represents a product revision, specification change, or extraction issue.
- **communication_interface** (high): The value for 'communication_interface' differs between the two source documents.
  - *Recommendation:* Review both source documents and determine whether the difference represents a product revision, specification change, or extraction issue.
- **euro_ef_ciency** (high): The value for 'euro_ef_ciency' differs between the two source documents.
  - *Recommendation:* Review both source documents and determine whether the difference represents a product revision, specification change, or extraction issue.
- **grid_connection_standard** (high): The value for 'grid_connection_standard' differs between the two source documents.
  - *Recommendation:* Review both source documents and determine whether the difference represents a product revision, specification change, or extraction issue.
- **safety_emc_standard** (high): The value for 'safety_emc_standard' differs between the two source documents.
  - *Recommendation:* Review both source documents and determine whether the difference represents a product revision, specification change, or extraction issue.

## Brief Checklist Coverage

| Checklist item | Covered? | Notes |
|---|---|---|
| Product Identity | Yes (1 field(s)) | Target model/variant is identified; model-code differences are surfaced for review. |
| Manufacturer Identity | Yes (0 field(s)) | Manufacturer identity is part of the source evidence; verify legal/factory details against the final supplier documents. |
| Test Evidence | Yes (2 field(s)) | Standards/compliance claims are extracted where present. Actual test certificates are not included in the datasheets and must be requested. |
| Labeling | Yes (0 field(s)) | Label-relevant information such as model, ratings and ingress protection is reported. Physical nameplate artwork/photos are not provided. |
| Importer Paperwork | Yes (0 field(s)) | Importer-side customs/commercial paperwork is outside the supplied datasheets and is explicitly flagged as follow-up. |

## Specifications

### Electrical Specifications

| Field | Source 1 | Source 2 | Status |
|---|---|---|---|
| Max Ac Output Apparent Power Kva | — | 5.5 kVA | Only in source 2 — unconfirmed |
| Max Active Power Kw | 5.5 kW | — | Only in source 1 — unconfirmed |
| Max Dc Input Power Kw | 6.5 kW | — | Only in source 1 — unconfirmed |
| Max Input Short Circuit Current A | — | 3 A | Only in source 2 — unconfirmed |
| Max Operating Pv Input Current A | — | 19.5+19.5 A | Only in source 2 — unconfirmed |
| Max Pv Input Power Kw | — | 5.2 kW | Only in source 2 — unconfirmed |
| Max Pv Input Voltage V | — | 1100 V | Only in source 2 — unconfirmed |
| Mppt Voltage Range V | — | 120-1000 V | Only in source 2 — unconfirmed |
| No Of Mpp Trackers | 2 | — | Only in source 1 — unconfirmed |
| No Of Mpp Trackers No Of Strings Per Mpp Tracker | — | 2/1+1 | Only in source 2 — unconfirmed |
| Rated Ac Output Active Power Kw | — | 5 kW | Only in source 2 — unconfirmed |
| Rated Output Power Kw | 5 kW | — | Only in source 1 — unconfirmed |
| Rated Output Voltage Range V | 7.6/7.3 V | 220/380V, 230/400V V | ⚠ Conflicting values between sources |
| Rated Pv Input Voltage V | — | 13+13 V | Only in source 2 — unconfirmed |
| Start Up Voltage V | — | 600 V | Only in source 2 — unconfirmed |

### Performance

| Field | Source 1 | Source 2 | Status |
|---|---|---|---|
| Euro Ef Ciency | 98.3% % | 98% % | ⚠ Conflicting values between sources |
| Max Ef Ciency | 98.5% % | 98.5% % | Confirmed (both sources agree) |

### Protection Features

| Field | Source 1 | Source 2 | Status |
|---|---|---|---|
| Ac Output Overcurrent Protection | Yes | Yes | Confirmed (both sources agree) |
| Ac Output Overvoltage Protection | Yes | Yes | Confirmed (both sources agree) |
| Ac Short Circuit Protection | Yes | Yes | Confirmed (both sources agree) |
| Anti Islanding Protection | Yes | — | Only in source 1 — unconfirmed |
| Dc Injection Current | — | <0.5%ln | Only in source 2 — unconfirmed |
| Dc Reverse Polarity Protection | Yes | — | Only in source 1 — unconfirmed |
| Ground Fault Monitoring | Yes | — | Only in source 1 — unconfirmed |
| Insulation Resistance Protection | Yes | — | Only in source 1 — unconfirmed |
| Surge Protection | No | — | Only in source 1 — unconfirmed |
| Temperature Protection | Yes | Yes | Confirmed (both sources agree) |

### Standards & Certifications

| Field | Source 1 | Source 2 | Status |
|---|---|---|---|
| Grid Connection Standard | IEC 61727, IEC 62116, EN 50549 | IEC/EN 61000-6-1/2/3/4, IEC/EN 62109-1, IEC/EN 62109-2 | ⚠ Conflicting values between sources |
| Safety Emc Standard | IEC/EN 61000-6-1/2/3/4, IEC/EN 62109-1, IEC/EN 62109-2 | IEC 61727, IEC 62116, CEI 0-21, EN 50549, NRS 097, RD 140, UNE 217002, OVE-Richtlinie R25, G99, VDE-AR-N 4105 | ⚠ Conflicting values between sources |

### General Data

| Field | Source 1 | Source 2 | Status |
|---|---|---|---|
| Cabinet Size Wxhxd Mm | 283×463×178 (Excluding connectors and brackets) mm | — | Only in source 1 — unconfirmed |
| Cooling Concept | Free Cooling | Natural Cooling | ⚠ Conflicting values between sources |
| Ingress Protection | IP65 | IP 65 | ⚠ Conflicting values between sources |
| Integrated Dc Switch | Yes | — | Only in source 1 — unconfirmed |
| Internal Consumption | <1W (Night) W | — | Only in source 1 — unconfirmed |
| Noise Db | — | <45 dB | Only in source 2 — unconfirmed |
| Noise Emission Typical | <45 dB dB | — | Only in source 1 — unconfirmed |
| Operating Humidity | 0-100% % | 0-100% % | Confirmed (both sources agree) |
| Operating Temperature Range | -25 to +60℃, >45℃ Derating °C | — | Only in source 1 — unconfirmed |
| Operating Temperature Range C | — | -25 to +60℃, >45℃ Derating °C | Only in source 2 — unconfirmed |
| Permissible Altitude M | 4000 m | 4000m m | ⚠ Conflicting values between sources |
| Topology | Transformerless | — | Only in source 1 — unconfirmed |
| Warranty | 5 Years year | 5 Years year | Confirmed (both sources agree) |
| Weight Kg | 11 kg | 4.8 kg | ⚠ Conflicting values between sources |

### Interface

| Field | Source 1 | Source 2 | Status |
|---|---|---|---|
| Communication Interface | RS485/RS232/Wiﬁ/LAN | RS485/RS232 /WiFi/LAN | ⚠ Conflicting values between sources |
| Display | LCD1602 | — | Only in source 1 — unconfirmed |
| Remote Operating Parameter Change | Yes | — | Only in source 1 — unconfirmed |
| Remote Software Upload | Yes | — | Only in source 1 — unconfirmed |

## What's Still Unclear

- **max_ac_output_apparent_power_kva** (low, source_2_only): 'max_ac_output_apparent_power_kva' appears in only one of the two source documents.
- **max_active_power_kw** (low, source_1_only): 'max_active_power_kw' appears in only one of the two source documents.
- **max_dc_input_power_kw** (low, source_1_only): 'max_dc_input_power_kw' appears in only one of the two source documents.
- **max_input_short_circuit_current_a** (low, source_2_only): 'max_input_short_circuit_current_a' appears in only one of the two source documents.
- **max_operating_pv_input_current_a** (low, source_2_only): 'max_operating_pv_input_current_a' appears in only one of the two source documents.
- **max_pv_input_power_kw** (low, source_2_only): 'max_pv_input_power_kw' appears in only one of the two source documents.
- **max_pv_input_voltage_v** (low, source_2_only): 'max_pv_input_voltage_v' appears in only one of the two source documents.
- **mppt_voltage_range_v** (low, source_2_only): 'mppt_voltage_range_v' appears in only one of the two source documents.
- **no_of_mpp_trackers** (low, source_1_only): 'no_of_mpp_trackers' appears in only one of the two source documents.
- **no_of_mpp_trackers_no_of_strings_per_mpp_tracker** (low, source_2_only): 'no_of_mpp_trackers_no_of_strings_per_mpp_tracker' appears in only one of the two source documents.
- **rated_ac_output_active_power_kw** (low, source_2_only): 'rated_ac_output_active_power_kw' appears in only one of the two source documents.
- **rated_output_power_kw** (low, source_1_only): 'rated_output_power_kw' appears in only one of the two source documents.
- **rated_pv_input_voltage_v** (low, source_2_only): 'rated_pv_input_voltage_v' appears in only one of the two source documents.
- **start_up_voltage_v** (low, source_2_only): 'start_up_voltage_v' appears in only one of the two source documents.
- **cabinet_size_wxhxd_mm** (low, source_1_only): 'cabinet_size_wxhxd_mm' appears in only one of the two source documents.
- **integrated_dc_switch** (low, source_1_only): 'integrated_dc_switch' appears in only one of the two source documents.
- **internal_consumption** (low, source_1_only): 'internal_consumption' appears in only one of the two source documents.
- **noise_db** (low, source_2_only): 'noise_db' appears in only one of the two source documents.
- **noise_emission_typical** (low, source_1_only): 'noise_emission_typical' appears in only one of the two source documents.
- **operating_temperature_range** (low, source_1_only): 'operating_temperature_range' appears in only one of the two source documents.
- **operating_temperature_range_c** (low, source_2_only): 'operating_temperature_range_c' appears in only one of the two source documents.
- **topology** (low, source_1_only): 'topology' appears in only one of the two source documents.
- **display** (low, source_1_only): 'display' appears in only one of the two source documents.
- **remote_operating_parameter_change** (low, source_1_only): 'remote_operating_parameter_change' appears in only one of the two source documents.
- **remote_software_upload** (low, source_1_only): 'remote_software_upload' appears in only one of the two source documents.
- **anti_islanding_protection** (low, source_1_only): 'anti_islanding_protection' appears in only one of the two source documents.
- **dc_injection_current** (low, source_2_only): 'dc_injection_current' appears in only one of the two source documents.
- **dc_reverse_polarity_protection** (low, source_1_only): 'dc_reverse_polarity_protection' appears in only one of the two source documents.
- **ground_fault_monitoring** (low, source_1_only): 'ground_fault_monitoring' appears in only one of the two source documents.
- **insulation_resistance_protection** (low, source_1_only): 'insulation_resistance_protection' appears in only one of the two source documents.
- **surge_protection** (low, source_1_only): 'surge_protection' appears in only one of the two source documents.

## Summary

Product: SUN-5K-G06P3-EU-AM2-P1. Compared 47 specification fields across 2 source documents. 7 fields agree. 9 fields conflict. 18 fields appear only in source 1. 13 fields appear only in source 2. 41 item(s) require human review. Overall assessment status: conflict.
