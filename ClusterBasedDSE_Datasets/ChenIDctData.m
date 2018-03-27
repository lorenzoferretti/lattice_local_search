function [data, featureSets, discretizedFeatureSets] = ChenIDctData(path, normalizeData)
% This function extract data from the ChenIDct database and prepare data 
% for the exploration. In a online exploration scenario, data will not 
% contain area and latency informations since these will be obtained as
% result of the synthesis process.

    conn = sqlite(which(strcat(path, '/ChenIDct.db')),'readonly');    
    ChenIDct_data = fetch(conn,'SELECT * FROM ChenIDct');
    ChenIDct_data(:,1) = [];
    latencies = [ChenIDct_data{:,1}];
    intervals = [ChenIDct_data{:,2}];
    ffs = [ChenIDct_data{:,3}];
    luts = [ChenIDct_data{:,4}];
    colums_loops = [ChenIDct_data{:,5}];
    row_loops = [ChenIDct_data{:,6}];
    accuracy_loops = [ChenIDct_data{:,7}];
    bundleA = [ChenIDct_data{:,8}];
    bundleB = [ChenIDct_data{:,9}];
    data = [double(latencies).' double(intervals).' double(ffs).' double(luts).' double(colums_loops).' double(row_loops).' double(accuracy_loops).' double(bundleA).' double(bundleB).'];

    close(conn)

    clear conn;
    clearvars ChenIDct_data latencies intervals ffs luts colums_loops row_loops accuracy_loops bundleA bundleB;
    
    %% Clean not useful data 
    % TODO: automate this process
    % Data contains: latencies intervals ffs luts colums_loops row_loops accuracy_loops bundleA bundleB
    % Since bundleA never changes it is removed because it has zero standard
    % deviation, also intevals and luts are removed for testing since we are interested in Area(FF) and Latenecy. 

    data(:,2) = [];
    data(:,3) = [];
    data(:,6)= [];

    % featureSets contains the information related to the daset.
    % For each feature we store in a list all the admissible values we want
    % to consider during the exploration
    featureSets = {};
    featureSets{1} = [0,2,4,8];
    featureSets{2} = [0,2,4,8];
    featureSets{3} = [0,2,4,8,16,32,64];
    featureSets{4} = [0,1];
    discretizedFeatureSets = discretizeSet(featureSets);

    if normalizeData
        data(:,3:end) = discretizeFeature(featureSets,discretizedFeatureSets,data(:,3:end));
        maxVal = max(data(:,1:2));
        data(:,1:2) = data(:,1:2)./maxVal;
    end

end
