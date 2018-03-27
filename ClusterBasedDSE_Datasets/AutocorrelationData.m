function [data, featureSets, discretizedFeatureSets] = AutocorrelationData(path,resize)
% This function extract data from the Autocorrelation database and prepare data 
% for the exploration. In a online exploration scenario, data will not 
% contain area and latency informations since these will be obtained as
% result of the synthesis process. 
%     exist(strcat('dataSampled_500sample_',num2str(percentage),'percent_',benchNames{b},'.mat'), 'file')  

    strcat(path, '/Autocorrelation.db')
    exist(strcat(path, '/Autocorrelation.db'),'file')
    conn = sqlite(which(strcat(path, '/Autocorrelation.db')),'readonly');
    ChenIDct_data = fetch(conn,'SELECT * FROM Autocorrelation');
    ChenIDct_data(:,1) = [];
    latencies = [ChenIDct_data{:,1}];
    intervals = [ChenIDct_data{:,2}];
    ffs = [ChenIDct_data{:,3}];
    luts = [ChenIDct_data{:,4}];
    max_loop = [ChenIDct_data{:,5}];
    gsm_resc_loop = [ChenIDct_data{:,6}];
    init_loop = [ChenIDct_data{:,7}];
    compute_loop = [ChenIDct_data{:,8}];
    shift_loop = [ChenIDct_data{:,9}];
    bundleA = [ChenIDct_data{:,10}];
    bundleB = [ChenIDct_data{:,11}];
    data = [double(latencies).' double(intervals).' double(ffs).' double(luts).' double(max_loop).' double(gsm_resc_loop).' double(init_loop).' double(compute_loop).' double(shift_loop).' double(bundleA).' double(bundleB).'];

    close(conn)

    clear conn;
    clearvars ChenIDct_data latencies intervals ffs luts colums_loops row_loops accuracy_loops bundleA bundleB;
    
    %% Clean unuseful data 
    % TODO: automate this process
    % Data has this format: latencies intervals ffs luts colums_loops row_loops accuracy_loops bundleA bundleB
    % Since bundleA never changes it is removed because it has zero standard
    % deviation, also intevals and luts are removed for testing.

    data(:,2) = [];
    data(:,3) = [];
    data(:,8)= [];

    % featureSets contains the information related to the daset.
    % For each feature we store in a list all the admissible values we want
    % to consider during the exploration    
    featureSets = {};
    featureSets{1} = [0,4,16,40,80,160];
    featureSets{2} = [0,4,16,40,80,160];
    featureSets{3} = [0,9];
    featureSets{4} = [0,4,19,38,76,152];
    featureSets{5} = [0,9];
    featureSets{6} = [0,1];
    discretizedFeatureSets = discretizeSet(featureSets);

    dataCol = size(data,2);

    if resize
        data(:,3:dataCol) = discretizeFeature(featureSets,discretizedFeatureSets,data(:,3:dataCol));
        maxVal = max(data(:,1:2));
        data(:,1:2) = data(:,1:2)./maxVal;
        %axis_limit = [min(data(:,1))-0.1 max(data(:,1))+0.1 min(data(:,2))-0.1 max(data(:,2))+0.1];
    else
        %axis_limit = [min(data(:,1))-100 max(data(:,1))+100 min(data(:,2))-1000 max(data(:,2))+1000];
    end

end
